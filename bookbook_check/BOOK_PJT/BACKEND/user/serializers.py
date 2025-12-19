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

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # ⭐️ 프론트엔드에 필요한 필드만 포함
        fields = ('id', 'email', 'name', 'selected_voice', 'selected_category')


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source='name', required=False)
    class Meta:
        model = CustomUser
        # 클라이언트가 수정 요청을 보낼 수 있는 필드와 조회 필드를 지정
        fields = ('nickname', 'selected_voice', 'email') 
        read_only_fields = ('email',) # 이메일은 수정 불가

    def validate_nickname(self, value):
        # 닉네임이 변경되었고, 이미 존재하는지 확인 (Unique 검사)
        request = self.context.get('request')
        user = request.user if request else None
        
        # 현재 사용자(user)를 제외하고, 동일한 name이 DB에 존재하는지 확인
        if CustomUser.objects.filter(name=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
        return value