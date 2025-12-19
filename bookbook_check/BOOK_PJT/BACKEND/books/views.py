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
        bestsellers = Book.objects.filter(is_bestseller=True).order_by('-id')[:20]
        
        # 목록 형태로 시리얼라이즈
        serializer = BookListSerializer(bestsellers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


User = get_user_model() # Django 기본 User 모델을 가져옵니다.

    

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
        serializer.save(user=self.request.user, book=book)


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