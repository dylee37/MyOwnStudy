from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer
from .models import CustomUser

class UserSignupSerializer(serializers.ModelSerializer):
    # password_confirm 필드는 모델에는 없지만 유효성 검사를 위해 추가
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'name',
            'password',
            'password_confirm', # Serializer에서만 사용
            'selected_voice',
            'favorite_book',
            'selected_category'
        )
        extra_kwargs = {
            'password': {'write_only': True}, # 비밀번호는 응답에 포함하지 않음
            'favorite_book': {'required': False}, # 명세에 따라 선택 사항으로 설정
        }

    # 비밀번호 일치 및 모델 저장을 위한 검증 로직
    def validate(self, data):
        if data.get('password') != data.pop('password_confirm'):
            raise serializers.ValidationError({"password_confirm": "비밀번호가 일치하지 않습니다."})
        return data

    def create(self, validated_data):
        # User 모델의 create_user 메서드를 사용하여 안전하게 비밀번호를 해시 저장
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            selected_voice=validated_data['selected_voice'],
            favorite_book=validated_data.get('favorite_book'),
            selected_category=validated_data['selected_category']
        )
        return user
    

class AuthTokenCustomSerializer(AuthTokenSerializer):
    # AbstractUser의 기본 'username' 대신 'email'을 필드로 지정
    email = serializers.EmailField(label="Email") 
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    # 기본 'username' 필드를 None으로 오버라이드
    username = None 

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # CustomUser.objects.filter를 사용하여 이메일로 사용자 찾기
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                user = None

            if user:
                if user.check_password(password):
                    # 인증 성공
                    attrs['user'] = user
                    return attrs
        
        # 인증 실패 시 에러 발생
        msg = '이메일 또는 비밀번호가 일치하지 않습니다.'
        raise serializers.ValidationError(msg, code='authorization')