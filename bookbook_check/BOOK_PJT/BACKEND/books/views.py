import random
from rest_framework import generics, status, permissions
from django.conf import settings
from .models import Book, Comment
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

        # 3. 유사도 점수 기준으로 정렬 및 상위 N개 선택
        # 코사인 유사도 점수가 높은 순서(내림차순)로 정렬
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        # 상위 10개 추천 도서 선택 (N=10)
        recommended_items = similarities[:10]
        
        # 4. 결과 시리얼라이즈 및 반환
        recommended_books = [item['book'] for item in recommended_items]
        
        # 임베딩 결과를 시각적으로 표현하기 어려워 다이어그램 생략 
        serializer = BookListSerializer(recommended_books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    



class BestsellerListView(APIView):
    """
    LLM이 선정한 베스트셀러 20권 목록을 반환합니다.
    URL: GET /api/books/bestsellers/
    """
    def get(self, request, format=None):
        # is_bestseller 필드가 True인 책만 필터링 (최대 20권)
        # 1. 일단 DB 확인
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


        
        # 목록 형태로 시리얼라이즈
        serializer = BookListSerializer(bestsellers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    




User = get_user_model() # Django 기본 User 모델을 가져옵니다.


class RecommendationView(APIView):
    """
    사용자 맞춤형 도서 추천을 제공합니다.
    - 로그인 사용자: LLM을 통해 취향(선호 카테고리, 좋아하는 책)에 맞는 2권 추천
    - 로그아웃 사용자: 베스트셀러 중 2권 랜덤 추천
    URL: GET /api/books/recommendations/
    """
    permission_classes = [permissions.AllowAny] # 인증 여부에 관계없이 접근 허용

    def get(self, request, format=None):
        # 1. 사용자 인증 여부 확인
        if request.user.is_authenticated:
            # --- 로그인 사용자 로직 ---
            user = request.user
            
            # 사용자 정보 추출 (실제 필드 사용)
            user_info = {
                "name": user.name,
                "preferred_category": user.selected_category,
                "favorite_book": user.favorite_book or "특정 책 없음"
            }

            # LLM 프롬프트 구성
            prompt = f"""
            당신은 사용자의 취향에 딱 맞는 책을 기가 막히게 찾아주는 전문 큐레이터입니다.
            아래 사용자 프로필을 보고, 좋아할 만한 **책 2권**을 추천해주세요.
            
            # 사용자 프로필
            - 이름: {user_info['name']}
            - 선호 카테고리: {user_info['preferred_category']}
            - 최근 관심 책: {user_info['favorite_book']}

            # 추천 규칙
            1. 응답은 'recommendations' 키를 가진 JSON 객체여야 합니다.
            2. 각 추천은 'book_id'(정수)와 'reason'(추천 이유)을 포함해야 합니다.
            3. 추천 이유는 사용자의 프로필(이름, 선호 카테고리, 관심 책)을 근거로 개인화된 메시지를 작성해야 합니다.
            4. 시스템에 등록된 책 중에서 추천해야 합니다.
            
            응답 예시:
            {{
                "recommendations": [
                    {{"book_id": 123, "reason": "{user_info['name']}님, {user_info['preferred_category']} 분야를 좋아하셔서 이 책을 추천해요."}},
                    {{"book_id": 456, "reason": "'{user_info['favorite_book']}'을 재미있게 읽으셨다면, 비슷한 분위기의 이 책도 분명 마음에 드실 거예요."}}
                ]
            }}
            """

            # LLM 호출 및 결과 처리
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
                
                # 만약 LLM이 2권을 추천하지 않았을 경우를 대비하여 랜덤 베스트셀러로 채움
                while len(final_recommendations) < 2:
                    bestsellers = list(Book.objects.filter(is_bestseller=True))
                    if not bestsellers: break # 베스트셀러가 없으면 중단
                    
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
                # 베스트셀러가 2권 미만일 경우, 있는 만큼만 반환
                random_books = bestsellers

            serializer = BookListSerializer(random_books, many=True)
            
            # 로그아웃 유저를 위한 추천 이유 추가
            final_data = []
            for book_data in serializer.data:
                final_data.append({
                    "book": book_data,
                    "reason": "지금 많은 사람들이 읽고 있는 베스트셀러입니다."
                })
                
            return Response(final_data, status=status.HTTP_200_OK)

class CommentCreateView(generics.CreateAPIView):
    """
    특정 도서에 대한 댓글을 등록합니다.
    URL: POST /api/books/<int:book_pk>/comments/
    # ⭐️ URL에서 책 ID를 'book_pk'로 받도록 통일 권장 ⭐️
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated] 

    def perform_create(self, serializer):
        book_id = self.kwargs.get('book_pk') # URLconf에서 book_pk를 사용하도록 변경 가정
        book = get_object_or_404(Book, pk=book_id)
        # serializer.save(user=self.request.user, book=book)
        user_voice = self.request.user.selected_voice
        
        serializer.save(
            user=self.request.user, 
            book=book, 
            voice_choice=user_voice  # 댓글 객체에 목소리 고정 저장
        )


# ⭐️⭐️ [최종 수정] 댓글 삭제 View: 'book_pk'와 'pk' 충돌 해결 ⭐️⭐️
class CommentDestroyView(generics.DestroyAPIView):
    """
    특정 도서에 속한 댓글을 삭제합니다.
    URL: DELETE /api/books/<int:book_pk>/comments/<int:pk>/
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer 
    permission_classes = [permissions.IsAuthenticated]

    # DRF가 URL에서 댓글 ID를 찾을 때 사용할 인자 이름을 'pk'로 설정합니다.
    # 즉, URL의 마지막 <int:pk>는 댓글 ID가 됩니다. (기본값)
    lookup_url_kwarg = 'pk' 

    def get_object(self):
        # 1. URL 인자 가져오기
        book_pk = self.kwargs.get('book_pk') # 책 ID (URL에서 명시적으로 분리)
        comment_pk = self.kwargs.get(self.lookup_url_kwarg) # 댓글 ID (URL에서 pk로 받음)

        # 2. 책과 댓글 ID로 객체 조회
        comment = get_object_or_404(
            Comment, 
            pk=comment_pk, 
            book__pk=book_pk # 해당 책에 속하는지 검증
        )
        
        # 3. 권한 확인 (본인이 작성한 댓글만 삭제 가능)
        if comment.user != self.request.user:
            raise PermissionDenied("자신이 작성한 댓글만 삭제할 수 있습니다.")
            
        return comment
    

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

            # ⭐️ 라이브러리 대신 직접 POST 요청 ⭐️
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