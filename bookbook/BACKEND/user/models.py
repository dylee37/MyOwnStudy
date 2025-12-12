from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        # REQUIRED_FIELDS에 포함된 필드들이 superuser 생성 시 누락되지 않도록
        # 기본값을 설정하거나 create_user에 인자로 전달해야 합니다.
        extra_fields.setdefault('name', 'admin') 
        extra_fields.setdefault('selected_voice', 'voice1')
        extra_fields.setdefault('selected_category', '소설/시/희곡')
        
        return self.create_user(email, password, **extra_fields)

# 목소리 옵션 & 카테고리 옵션 정의 (모델 필드의 Choices로 사용)
VOICE_CHOICES = [
    ('voice1', '목소리 1 (여성, 차분한)'),
    ('voice2', '목소리 2 (남성, 활기찬)'),
    ('voice3', '목소리 3 (여성, 에너지 넘치는)'),
    ('voice4', '목소리 4 (남성, 따뜻한)'),
]

# 프론트엔드 CATEGORIES와 일치해야 함
CATEGORY_CHOICES = [
    ('소설/시/희곡', '소설/시/희곡'),
    ('경제/경영', '경제/경영'),
    ('자기계발', '자기계발'),
    ('인문/교양', '인문/교양'),
    ('취미/실용', '취미/실용'),
    ('어린이/청소년', '어린이/청소년'),
    ('과학', '과학'),
]

class CustomUser(AbstractUser):
    username = None
    objects = CustomUserManager()
    # AbstractUser에는 username, first_name, last_name, email, password 필드가 이미 포함되어 있음

    # name 필드 (프론트엔드 닉네임)
    name = models.CharField(max_length=150, blank=False, unique=True, verbose_name="닉네임")

    # email 필드를 username 대신 로그인에 사용하기 위해 unique=True 설정
    email = models.EmailField(unique=True, blank=False)

    # 추가 필드
    selected_voice = models.CharField(
        max_length=20,
        choices=VOICE_CHOICES,
        default='voice1',
        verbose_name="선택된 목소리"
    )

    favorite_book = models.CharField(
        max_length=100,
        blank=True,  # 선택 사항
        null=True,
        verbose_name="좋아하는 도서"
    )

    selected_category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        blank=False,
        verbose_name="선호 카테고리"
    )

    # 기본 username 필드를 제거하고 email을 사용자 이름 필드로 지정
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'selected_voice', 'selected_category']  # superuser 생성 시 필수 필드

    def __str__(self):
        return self.email