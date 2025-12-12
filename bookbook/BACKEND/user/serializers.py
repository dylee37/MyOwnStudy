from rest_framework import serializers
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