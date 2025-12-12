# user/views.py
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import UserSignupSerializer

class UserSignupView(generics.CreateAPIView):
    """
    회원가입을 처리하는 API View (POST 요청만 허용)
    """
    serializer_class = UserSignupSerializer
    # 인증되지 않은 사용자도 접근 가능하도록 설정
    permission_classes = [AllowAny]
    
    # CreateAPIView는 POST 요청을 받으면 자동으로 .create() 메서드를 실행합니다.