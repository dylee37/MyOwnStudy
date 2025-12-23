import random
from rest_framework import generics, status, permissions
from django.conf import settings
from .models import Book, Comment, Library
from .serializers import BookListSerializer, BookDetailSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import BookListSerializer, BookDetailSerializer, CommentSerializer
from .utils import get_embedding, calculate_cosine_similarity, get_llm_recommendation # utils 함수 사용
import numpy as np
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
import json
from openai import OpenAI
import requests
from rest_framework.authentication import TokenAuthentication



# 책 목록 조회 및 생성 (GET / POST)
class BookListView(generics.ListCreateAPIView):
    queryset = Book.objects.all().order_by('-pub_date') # 최신순 정렬 예시
    serializer_class = BookListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

# 책 상세 정보 조회 (GET /:id)
class BookDetailView(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer
    lookup_field = 'pk'
    permission_classes = [IsAuthenticatedOrReadOnly]



class RecommendedBooksView(APIView):
    """
    특정 책의 임베딩 벡터를 기반으로 유사한 도서 목록을 반환합니다.
    URL: GET /api/books/recommendations/<int:pk>/
    """
    def get(self, request, pk, format=None):
        try:
            # 1. 기준이 될 책(Source Book) 찾기
            source_book = Book.objects.get(pk=pk)
            
            # 임베딩 벡터가 없는 경우 에러 처리
            if not source_book.embedding_vector:
                return Response(
                    {"detail": "기준 도서의 임베딩 벡터가 없습니다. 임베딩 생성을 먼저 완료해야 합니다."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            source_vector = source_book.embedding_vector
            
        except Book.DoesNotExist:
            return Response(
                {"detail": "기준 도서를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. 모든 다른 책과 유사도 계산
        # QuerySet을 리스트로 변환하여 NumPy로 효율적으로 처리할 수 있도록 준비
        all_books = list(Book.objects.exclude(pk=pk).all()) 
        
        similarities = []
        for target_book in all_books:
            target_vector = target_book.embedding_vector
            
            # 임베딩 벡터가 있는 경우에만 유사도 계산
            if target_vector:
                similarity = calculate_cosine_similarity(source_vector, target_vector)
                
                similarities.append({
                    'book': target_book,
                    'similarity': similarity
                })

        # 3. 유사도 점수 기준으로 정렬 및 상위 10개 선택
        # 코사인 유사도 점수가 높은 순서(내림차순)로 정렬
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        recommended_items = similarities[:10]
        
        recommended_books = [item['book'] for item in recommended_items]
 
        serializer = BookListSerializer(recommended_books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class BestsellerListView(APIView):
    """
    LLM이 선정한 베스트셀러 20권 목록을 반환합니다.
    URL: GET /api/books/bestsellers/
    """
    def get(self, request, format=None):
        # is_bestseller 필드가 True인 책만 필터링
        # 1. DB 확인
        bestsellers = Book.objects.filter(is_bestseller=True)[:20]

        # 2. 비어있다면?
        if not bestsellers.exists():
            # 랜덤 200권 뽑기
            sample_books = Book.objects.all().order_by('?')[:200]
            
            # GPT에게 보낼 텍스트 생성
            books_data = "\n".join([f"ID:{b.id}, 제목:{b.title}, 저자:{b.author}" for b in sample_books])
            
            prompt = f"""
            당신은 도서 추천 전문가입니다. 아래 200권의 리스트 중 베스트셀러가 될 만한 20권을 선정하세요.
            반드시 아래 JSON 형식으로 응답하세요.
            {{ "recommendations": [ {{"book_id": ID값, "reason": "이유"}}, ... ] }}
            
            리스트:
            {books_data}
            """
            
            # GMS_KEY를 사용하여 GPT 호출
            llm_response = get_llm_recommendation(prompt)
            
            if llm_response:
                try:
                    res_data = json.loads(llm_response)
                    best_ids = list(set([item['book_id'] for item in res_data.get('recommendations', [])]))
                    
                    # DB에 저장해서 다음부터 GPT 안 써도 되도록
                    Book.objects.filter(id__in=best_ids).update(is_bestseller=True)

                    bestsellers = Book.objects.filter(is_bestseller=True).order_by('-id')[:20]
                except Exception as e:
                    print(f"JSON 파싱 에러: {e}")

        serializer = BookListSerializer(bestsellers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    




User = get_user_model()


class RecommendationView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):

        if request.user.is_authenticated:
            user = request.user
            
            candidate_books = Book.objects.filter(category__name=user.selected_category).order_by('?')[:20]
            
            if not candidate_books.exists() or candidate_books.count() < 5:
                print(f"DEBUG: {user.selected_category} 카테고리에 책이 부족하여 전체 도서에서 추출합니다.")
                candidate_books = Book.objects.all().order_by('?')[:20]

            books_list_str = "\n".join([
                f"ID:{b.id}, 제목:{b.title}, 저자:{b.author}, 카테고리:{b.category.name if b.category else '미지정'}" 
                for b in candidate_books
            ])

            user_info = {
                "name": user.name,
                "preferred_category": user.selected_category,
                "favorite_book": user.favorite_book or "특정 책 없음"
            }

            prompt = f"""
                당신은 도서 추천 전문가입니다. 아래 [후보 목록] 중에서 사용자의 취향에 가장 잘 맞는 책 2권을 선정하세요.

                [사용자 프로필]
                - 성함: {user_info['name']}
                - 선호 장르: {user_info['preferred_category']}
                - 최근 관심 책: {user_info['favorite_book']}

                [후보 목록]
                {books_list_str}

                [규칙]
                1. 반드시 위 [후보 목록]에 있는 ID만 사용하세요. 없는 ID를 지어내지 마세요.
                2. 선호 장르인 '{user_info['preferred_category']}'를 최우선으로 고려하세요.
                3. 친절하고 개인화된 추천사(reason)를 작성하세요.
                4. 반드시 JSON 형식으로 응답하세요:
                {{ "recommendations": [ {{"book_id": ID, "reason": "추천사"}}, ... ] }}
            """

            llm_response_json = get_llm_recommendation(prompt)
            
            if not llm_response_json:
                return Response({"detail": "맞춤 추천 생성에 실패했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            try:
                response_data = json.loads(llm_response_json)
                recommendations = response_data.get('recommendations', [])
                
                book_ids = [item['book_id'] for item in recommendations if 'book_id' in item]
                
                # N+1 문제 방지를 위해 `in_bulk` 사용
                books_map = Book.objects.in_bulk(book_ids)
                
                final_recommendations = []
                for item in recommendations:
                    book = books_map.get(item.get('book_id'))
                    if book:
                        book_data = BookListSerializer(book).data
                        final_recommendations.append({
                            "book": book_data,
                            "reason": item.get('reason', "추천 이유가 없습니다.")
                        })

                while len(final_recommendations) < 2:
                    bestsellers = list(Book.objects.filter(is_bestseller=True))
                    if not bestsellers: break 
                    
                    random_book = random.choice(bestsellers)
                    if not any(rec['book']['id'] == random_book.id for rec in final_recommendations):
                         final_recommendations.append({
                            "book": BookListSerializer(random_book).data,
                            "reason": "이런 책은 어떠세요? 지금 많은 사람들이 읽고 있는 베스트셀러입니다."
                        })

                return Response(final_recommendations[:2], status=status.HTTP_200_OK)

            except (json.JSONDecodeError, ValueError):
                return Response({"detail": "LLM 응답 처리 중 오류가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            # --- 로그아웃 사용자 로직 ---
            bestsellers = list(Book.objects.filter(is_bestseller=True))
            
            if len(bestsellers) >= 2:
                random_books = random.sample(bestsellers, 2)
            else:
                random_books = bestsellers

            serializer = BookListSerializer(random_books, many=True)

            final_data = []
            for book_data in serializer.data:
                final_data.append({
                    "book": book_data,
                    "reason": "지금 많은 사람들이 읽고 있는 베스트셀러입니다."
                })
                
            return Response(final_data, status=status.HTTP_200_OK)

class CommentCreateView(generics.CreateAPIView):
    """
    댓글을 작성하면 자동으로 서재(Library)에 등록되는 뷰
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        book_pk = self.kwargs.get('book_pk')
        book = get_object_or_404(Book, pk=book_pk)
        
        # 1. 댓글 저장
        serializer.save(user=self.request.user, book=book)
        
        # 2. 서재 등록 시 디버깅 정보 출력
        print(f"--- 서재 등록 시도 ---")
        print(f"유저: {self.request.user} (ID: {self.request.user.id})")
        print(f"도서: {book.title}")

        # 3. 유저와 도서를 연결하여 서재(Library)에 저장
        obj, created = Library.objects.get_or_create(
            user=self.request.user,
            book=book
        )
        print(f"등록 결과: {'새로 생성됨' if created else '이미 존재함'}")


class CommentDestroyView(generics.DestroyAPIView):
    """
    특정 도서에 속한 댓글을 삭제합니다.
    URL: DELETE /api/books/<int:book_pk>/comments/<int:pk>/
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer 
    permission_classes = [permissions.IsAuthenticated]

    # DRF가 URL에서 댓글 ID를 찾을 때 사용할 인자 이름을 'pk'로 설정
    # URL의 마지막 <int:pk>는 댓글 ID
    lookup_url_kwarg = 'pk' 

    def get_object(self):
        # 1. URL 인자 가져오기
        book_pk = self.kwargs.get('book_pk') # 책 ID (URL에서 명시적으로 분리)
        comment_pk = self.kwargs.get(self.lookup_url_kwarg) # 댓글 ID (URL에서 pk로 받음)

        # 2. 책과 댓글 ID로 객체 조회
        comment = get_object_or_404(
            Comment, 
            pk=comment_pk, 
            book__pk=book_pk
        )
        
        # 3. 권한 확인 (본인이 작성한 댓글만 삭제 가능)
        if comment.user != self.request.user:
            raise PermissionDenied("자신이 작성한 댓글만 삭제할 수 있습니다.")
            
        return comment

    def perform_destroy(self, instance):
        user = self.request.user
        book = instance.book
        
        # 1. 댓글 삭제
        instance.delete()
        print(f"--- 댓글 삭제 완료 (유저: {user}, 도서: {book.title}) ---")

        # 2. 해당 유저가 이 책에 남긴 다른 댓글이 더 있는지 확인
        remaining_comments = Comment.objects.filter(user=user, book=book).exists()

        # 3. 더 이상 남은 댓글이 없다면 서재에서도 삭제
        if not remaining_comments:
            Library.objects.filter(user=user, book=book).delete()
            print(f"--- 서재에서도 삭제 완료: {book.title} ---")
        else:
            print(f"--- 아직 다른 댓글이 남아있어 서재에 유지합니다 ---")
    

class TextToSpeechView(APIView):
    """
    텍스트와 선택된 목소리를 받아 OpenAI TTS API로 음성을 생성합니다.
    URL: POST /api/books/tts/
    """
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        text = request.data.get('text')
        voice_id = request.data.get('voice', 'voice1')
        
        # 프론트엔드 voice ID를 OpenAI 실제 목소리 이름으로 매핑
        voice_map = {
            'voice1': 'alloy',
            'voice2': 'echo',
            'voice3': 'shimmer',
            'voice4': 'onyx'
        }
        selected_voice = voice_map.get(voice_id, 'alloy')

        if not text:
            return Response({"detail": "텍스트가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            print(f"DEBUG: GMS_KEY is {settings.GMS_KEY[:5]}...")
            # settings에 정의된 GMS_KEY 사용
            gms_url = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/audio/speech"
            
            headers = {
                "Authorization": f"Bearer {settings.GMS_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini-tts",
                "input": text,
                "voice": selected_voice,
                "response_format": "mp3"
            }

            # 라이브러리 대신 직접 POST 요청
            response = requests.post(gms_url, headers=headers, json=payload)

            if response.status_code == 200:
                # 성공 시 오디오 파일 반환
                return HttpResponse(response.content, content_type="audio/mpeg")
            else:
                # GMS 서버에서 에러가 온 경우
                print(f"GMS ERROR: {response.status_code} - {response.text}")
                return Response(response.json(), status=response.status_code)
            
        except Exception as e:
            print(f"SERVER ERROR: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SpeechToTextView(APIView):
    """
    오디오 파일을 받아 Whisper-1 모델로 텍스트로 변환합니다.
    URL: POST /api/books/transcribe/
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        if 'audio' not in request.FILES:
            return Response({"error": "오디오 파일이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        audio_file = request.FILES['audio']

        try:
            client = OpenAI(api_key=settings.GMS_KEY, base_url="https://gms.ssafy.io/gmsapi/api.openai.com/v1")
            
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=(audio_file.name, audio_file.read(), audio_file.content_type),
                response_format="json"
            )
            
            transcribed_text = transcription.text
            
            return Response({"text": transcribed_text}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"STT ERROR: {str(e)}")
            return Response({"error": f"음성 변환 중 오류 발생: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class BookDocentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            book = get_object_or_404(Book, pk=pk)
            voice_id = request.data.get('voice', 'alloy')
            
            voice_map = {
                'voice1': 'alloy',
                'voice2': 'echo',
                'voice3': 'shimmer',
                'voice4': 'onyx'
            }
            selected_voice = voice_map.get(voice_id, voice_id)

            prompt = f"""
            당신은 '북북(BOOKBOOK)' 서비스의 전문 AI 도슨트입니다. 
            아래 도서 정보를 바탕으로, 마치 갤러리에서 책을 소개하듯 다정하고 몰입감 있는 오디오 스크립트를 작성해 주세요.

            [도서 정보]
            - 제목: {book.title}
            - 저자: {book.author}
            - 내용: {book.description}

            [작성 가이드라인]
            1. 인사와 도입: "안녕하세요, 오늘 여러분께 소개해 드릴 책은..."으로 시작하여 책의 첫인상을 묘사해 주세요.
            2. 핵심 요약: 책의 전체 내용을 요약하되, 딱딱한 나열이 아닌 이 책이 던지는 핵심 질문이나 감동 포인트를 중심으로 설명해 주세요. (3~4문장)
            3. 마무리: "이 책의 마지막 페이지를 덮을 때쯤 여러분은 어떤 생각을 하게 될까요?"와 같이 독자의 호기심을 자극하며 마쳐주세요.
            4. 어조: 반드시 '해요체'를 사용하여 부드럽고 따뜻하게 작성해 주세요. 전문 용어보다는 쉬운 단어를 사용하세요.
            5. 주의사항: 오디오로 읽힐 글이므로 문장이 너무 길지 않아야 하며, 한글 위주로 작성해 주세요.

            스크립트만 응답해 주세요.
            """
            summary_text = get_llm_recommendation(prompt)
            
            if not summary_text:
                return Response({"error": "요약 생성 실패"}, status=status.HTTP_400_BAD_REQUEST)

            gms_url = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/audio/speech"
            headers = {
                "Authorization": f"Bearer {settings.GMS_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-4o-mini-tts",
                "input": summary_text,
                "voice": selected_voice,
                "response_format": "mp3"
            }

            response = requests.post(gms_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                return HttpResponse(response.content, content_type="audio/mpeg")
            else:
                return Response(response.json(), status=response.status_code)

        except Exception as e:
            print(f"DOCENT ERROR: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
