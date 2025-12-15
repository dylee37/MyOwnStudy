from rest_framework import generics, status, permissions
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
import json

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

class PersonalizedRecommendationView(APIView):
    """
    로그인한 사용자 정보를 기반으로 LLM에게 2권의 맞춤형 도서를 추천받습니다.
    URL: GET /api/books/personalized-recommendation/
    """
    # ⭐️ 인증된 사용자만 접근 가능하도록 설정 ⭐️
    permission_classes = [IsAuthenticated] 

    def get(self, request, format=None):
        user = request.user
        
        # 1. 사용자 데이터 준비 (⭐️ 실제 User 모델에 따라 필드명 수정 필요 ⭐️)
        user_info = {
            "username": user.username,
            # 현재 기본 User 모델에는 선호 장르 같은 필드가 없으므로, 임시 데이터를 사용합니다.
            # 실제 구현 시, User 모델을 확장하여 '선호 장르' 같은 필드를 추가해야 합니다.
            "preferred_category": "소설/시/희곡", # 임시 값
            "activity_level": "높음", # 임시 값
        }
        
        # 2. LLM에게 전달할 프롬프트 구성 (DB 전체 책 데이터는 너무 크므로, 프롬프트에서 요청)
        prompt = f"""
        당신은 사용자의 취향에 맞는 책을 찾아주는 전문 큐레이터입니다.
        아래는 현재 로그인한 사용자의 프로필 정보입니다.
        
        사용자 프로필: {json.dumps(user_info, ensure_ascii=False)}
        
        사용자의 취향과 선호도를 고려하여, 사용자가 가장 좋아할 만한 **2권의 도서 ID와 해당 책을 추천하는 구체적인 이유**를 **JSON 리스트** 형태로 추천해 주세요.
        
        규칙:
        1. 응답은 오직 'recommendations'라는 키를 가진 JSON 객체 형태여야 합니다.
        2. 리스트 요소는 'book_id'(정수), 'reason'(문자열) 필드를 포함해야 합니다.
        3. 추천 책은 시스템에 등록된 책이어야 합니다 (ID 유효성).
        
        응답 예시:
        {{"recommendations": [ {{"book_id": 123, "reason": "OO님의 취향을 고려했을 때..."}}, ... ]}}
        """
        
        # 3. LLM API 호출
        llm_response_json = get_llm_recommendation(prompt)
        
        if not llm_response_json:
            return Response({"detail": "맞춤 추천 생성에 실패했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            response_data = json.loads(llm_response_json)
            recommendations = response_data.get('recommendations', [])
            
            # 4. 추천 받은 책 ID를 사용하여 DB에서 책 정보 조회
            book_ids = [item['book_id'] for item in recommendations if 'book_id' in item]
            recommended_books_map = {book.id: book for book in Book.objects.filter(id__in=book_ids)}
            
            # 5. 응답 데이터 구조화
            final_recommendations = []
            for item in recommendations:
                book = recommended_books_map.get(item.get('book_id'))
                if book:
                    # BookListSerializer를 사용하여 책 데이터 직렬화
                    book_data = BookListSerializer(book).data
                    final_recommendations.append({
                        "book": book_data,
                        "reason": item.get('reason', "LLM 추천 이유 없음")
                    })
            
            return Response(final_recommendations, status=status.HTTP_200_OK)
        
        except (json.JSONDecodeError, ValueError) as e:
            return Response({"detail": f"LLM 응답을 처리하는 데 실패했습니다: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

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