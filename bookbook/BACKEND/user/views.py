# user/views.py
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import UserSignupSerializer, AuthTokenCustomSerializer

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