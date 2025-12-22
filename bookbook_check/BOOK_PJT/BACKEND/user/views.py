# user/views.py
from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView 
from django.db.models import Avg, Count

from .serializers import UserSignupSerializer, AuthTokenCustomSerializer, CustomUserSerializer, UserProfileUpdateSerializer

from books.utils import get_llm_recommendation 
from books.models import Book, Library, Comment
from books.serializers import BookListSerializer

from .models import CustomUser
import json
import logging
logger = logging.getLogger(__name__)


class UserSignupView(generics.CreateAPIView):
    """
    회원가입을 처리하는 API View (POST 요청만 허용)
    """
    serializer_class = UserSignupSerializer
    # 인증되지 않은 사용자도 접근 가능하도록 설정
    permission_classes = [AllowAny]
    
    # CreateAPIView는 POST 요청을 받으면 자동으로 .create() 메서드를 실행합니다.

class UserLoginView(ObtainAuthToken):
    """
    로그인을 처리하고 인증 토큰과 함께 사용자 닉네임을 반환하는 API View.
    """
    serializer_class = AuthTokenCustomSerializer 

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # 1. 토큰 생성 또는 가져오기
        token, created = Token.objects.get_or_create(user=user)
        
        # 2. 닉네임과 토큰을 함께 응답
        return Response({
            'token': token.key,
            'user_name': user.name, 
            'email': user.email
        })
    

# 1. JWT 토큰 발급 시 사용자 정보 추가
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # 부모 클래스의 validate 호출 (토큰 생성)
        data = super().validate(attrs)
        
        # ⭐️ CustomUserSerializer를 사용하여 사용자 정보 직렬화
        user_serializer = CustomUserSerializer(self.user)
        
        # 응답 데이터에 사용자 정보 추가
        data['user'] = user_serializer.data 
        
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


    # 사용자 정보 및 통계 반환 (GET /api/v1/user/me/)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_me(request):
    user = request.user
    
    # 1. 읽은 책 권 수
    books_read = Library.objects.filter(user=user).count()
    
    # 2. 작성한 댓글 개수
    comments_count = Comment.objects.filter(user=user).count()
    
    # 3. 평균 평점 (내가 작성한 모든 댓글의 평점 평균)
    avg_rating_data = Comment.objects.filter(user=user).aggregate(Avg('rating'))
    average_rating = avg_rating_data['rating__avg'] or 0.0
    
    # 0.5 단위 등으로 깔끔하게 보이게 하고 싶다면 round 사용
    average_rating = round(average_rating, 1)
    
    stats_data = {
        'books_read': books_read,
        'comments_count': comments_count,
        'average_rating': average_rating,
    }
    
    data = {
        'id': user.id,
        'email': user.email,
        'name': user.name,  # 프론트엔드에서 userName.value = response.data.name; 로 사용 중
        'bio': user.bio,  # 추가
        'favorite_book': user.favorite_book,  # 추가
        'selected_category': user.selected_category,  # 추가
        'stats': stats_data,
        'selected_voice': user.selected_voice,
    }
    return Response(data)



# 라이브러리 책 목록 반환 (GET /api/v1/user/library/)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_library(request):
    # ⭐️⭐️ 임시 책 목록 데이터 (나중에 DB에서 실제 책 데이터를 가져와야 함) ⭐️⭐️
    
    # 현재 서재가 비어 있으므로 빈 배열을 반환합니다.
    library_books = [] 
    
    # 만약 임시로 작동을 확인하고 싶다면 아래와 같이 더미 데이터를 넣을 수 있습니다.
    # library_books = [
    #     {'id': 101, 'title': '임시 서재 도서 1', 'author': '작가 A', 'cover_url': 'url_to_cover'},
    #     {'id': 102, 'title': '임시 서재 도서 2', 'author': '작가 B', 'cover_url': 'url_to_cover'},
    # ]
    
    return Response(library_books)



# 회원 탈퇴 (DELETE /api/v1/user/delete/)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    user = request.user
    try:
        # ⭐️ 사용자 모델을 DB에서 실제로 삭제 ⭐️
        user.delete()
        # 성공 응답 (일반적으로 204 No Content 또는 성공 메시지)
        return Response({'message': '회원 탈퇴가 성공적으로 완료되었습니다.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    


class PersonalizedRecommendationView(APIView):
    """
    로그인한 사용자 정보를 기반으로 LLM에게 2권의 맞춤형 도서를 추천받습니다.
    URL: GET /api/v1/user/personalized-recommendation/
    """
    permission_classes = [IsAuthenticated] 

    def get(self, request, format=None):
        user = request.user
        
        # 1. LLM에 전달할 사용자 데이터와 전체 책 목록 구성
        # A. 사용자 프로필 (CustomUser 모델 필드 활용)
        user_info = {
            "name": user.name,
            "email": user.email,
            "selected_category": user.selected_category,
            "favorite_book": user.favorite_book,
            # (필요하다면 다른 필드도 추가)
        }
        
        # B. 전체 책 목록 (데이터 크기 제한 때문에 프롬프트에 넣을 수 없음 -> LLM에게 요청)
        
        # 2. LLM에게 전달할 프롬프트 구성
        prompt = f"""
        당신은 사용자의 취향에 맞는 책을 찾아주는 전문 큐레이터입니다.
        
        **사용자 프로필:** {json.dumps(user_info, ensure_ascii=False)}
        
        사용자의 선호 장르('{user.selected_category}')와 좋아하는 책('{user.favorite_book}')을 포함한 프로필을 분석하여, 사용자가 가장 좋아할 만한 **2권의 도서 ID와 해당 책을 추천하는 구체적인 이유**를 **JSON 리스트** 형태로 추천해 주세요.
        
        규칙:
        1. 응답은 오직 'recommendations'라는 키를 가진 JSON 객체 형태여야 합니다.
        2. 리스트 요소는 'book_id'(정수)와 'reason'(문자열) 필드를 포함해야 합니다.
        3. 추천 책은 **시스템에 등록된 유효한 책 ID**를 사용해야 합니다.
        4. **전체 도서 목록을 알 수 없으므로, 한국 시장의 베스트셀러 및 트렌드를 기반으로 ID를 유추하여 추천해 주세요.** (나중에 DB에서 유효성 검사)
        
        응답 예시:
        {{"recommendations": [ {{"book_id": 123, "reason": "{user.name}님의 취향을 고려했을 때..."}}, ... ]}}
        """
        
        # 3. LLM API 호출
        llm_response_json = get_llm_recommendation(prompt)
        
        if not llm_response_json:
            logger.error(f"LLM API 호출 실패: 사용자 ID {user.id}")
            return Response({"detail": "맞춤 추천 생성에 실패했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            response_data = json.loads(llm_response_json)
            recommendations = response_data.get('recommendations', [])
            
            # 4. 추천 받은 책 ID를 사용하여 DB에서 책 정보 조회 및 유효성 검사
            book_ids = [item['book_id'] for item in recommendations if 'book_id' in item and isinstance(item['book_id'], int)]
            
            # DB에 실제로 존재하는 책만 필터링
            recommended_books_map = {book.id: book for book in Book.objects.filter(id__in=book_ids)}
            
            # 5. 응답 데이터 구조화
            final_recommendations = []
            for item in recommendations:
                book_id = item.get('book_id')
                book = recommended_books_map.get(book_id)
                
                if book:
                    # BookListSerializer를 사용하여 책 데이터 직렬화
                    book_data = BookListSerializer(book).data
                    final_recommendations.append({
                        "book": book_data,
                        # LLM이 제공한 추천 이유를 포함
                        "reason": item.get('reason', f"{user.name}님에게 추천합니다.")
                    })
            
            # LLM이 2권을 추천했지만 DB에 유효한 책이 2권 미만일 수 있음.
            return Response(final_recommendations, status=status.HTTP_200_OK)
        
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"LLM 응답 JSON 처리 실패: {e}, 응답 텍스트: {llm_response_json[:200]}...")
            return Response({"detail": f"LLM 응답을 처리하는 데 실패했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class UserProfileUpdateView(generics.RetrieveUpdateAPIView):
    """
    인증된 사용자의 프로필 정보(닉네임, 목소리 등)를 조회(GET)하고 부분 수정(PATCH)합니다.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileUpdateSerializer 
    queryset = CustomUser.objects.all()

    def get_object(self):
        # 요청을 보낸 인증된 사용자(request.user) 객체를 반환합니다.
        return self.request.user

    # 부분 업데이트를 위해 PUT 대신 PATCH를 명시적으로 선호합니다.
    def update(self, request, *args, **kwargs):
        # partial=True 설정으로 부분 업데이트 허용 (예: name만 보낼 수 있음)
        kwargs['partial'] = True 
        return super().update(request, *args, **kwargs)
    



class UserLibraryView(APIView):
    # 명시적으로 TokenAuthentication 설정
    authentication_classes = [TokenAuthentication] 
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Library.objects.filter(user=request.user).select_related('book')
        books = [item.book for item in qs]
        serializer = BookListSerializer(books, many=True)
        return Response(serializer.data)