# user/views.py
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from .serializers import UserSignupSerializer, AuthTokenCustomSerializer, UserProfileUpdateSerializer
from .models import CustomUser

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

class AccountDeleteView(generics.DestroyAPIView):
    """
    인증된 사용자의 계정을 삭제하는 API View (DELETE 요청만 허용).
    """
    # 인증된 사용자만 접근 가능
    permission_classes = [IsAuthenticated]
    
    # CustomUser 모델을 사용
    queryset = CustomUser.objects.all()

    def get_object(self):
        # 요청을 보낸 인증된 사용자(request.user) 객체를 반환
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # 실제 사용자 계정 삭제
        self.perform_destroy(instance)
        
        # 204 No Content 응답 (성공적으로 삭제되었으나 응답 본문은 없음)
        return Response(status=status.HTTP_204_NO_CONTENT)
    

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