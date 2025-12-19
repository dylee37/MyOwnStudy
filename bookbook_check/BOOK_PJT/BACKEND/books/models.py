from django.db import models
from django.contrib.postgres.fields import ArrayField # 임베딩 벡터용
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    """도서의 카테고리 (예: 소설, 경제/경영, 판타지 등)"""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    """도서 상세 정보를 저장하는 모델"""
    # ⭐️ 필수 정보
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=50)
    publisher = models.CharField(max_length=50)
    isbn = models.CharField(max_length=13, unique=True)
    cover = models.URLField()
    pub_date = models.DateField()
    
    # ⭐️ book.json에 포함된 추가 상세 정보
    description = models.TextField(blank=True, null=True)
    subTitle = models.CharField(max_length=255, blank=True, null=True)
    
    # ⭐️ 작가 정보
    author_info = models.TextField(blank=True, null=True)
    author_photo = models.URLField(blank=True, null=True)

    is_bestseller = models.BooleanField(default=False)
    
    # ⭐️ 카테고리 (Foreign Key 연결)
    # JSON에서 "category": 1 로 참조하므로 ForeignKey로 정의합니다.
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='books'
    )
    
    # ⭐️ 평점 (Aladin 리뷰 등 외부 평점)
    customer_review_rank = models.FloatField(default=0) # 0.0 ~ 10.0 사이의 값으로 가정



    # ⭐️⭐️ 임베딩 벡터를 저장할 필드 추가 ⭐️⭐️
    embedding_vector = models.JSONField(
        null=True, 
        blank=True, 
        help_text="OpenAI text-embedding-3-small 모델의 벡터 (1536차원) 저장 공간"
    )
    

    # ⭐️ Meta 정보
    class Meta:
        # 최근 출간일 순으로 기본 정렬
        ordering = ['-pub_date']

    def __str__(self):
        return self.title

# 참고: 나중에 댓글 기능을 구현할 때 Comment 모델이 이 파일 또는 별도 파일에 추가됩니다.

class Comment(models.Model):
    """도서에 대한 사용자 댓글/토크톡 모델"""
    # 어떤 책에 달린 댓글인지
    book = models.ForeignKey(
        'Book', # Book 모델을 문자열로 참조 (순환 참조 방지)
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    # 누가 작성한 댓글인지
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # 댓글 내용 (텍스트 또는 음성 파일 URI)
    content = models.TextField()
    rating = models.IntegerField(default=5) # 평점 (1~5점)
    is_voice = models.BooleanField(default=False) # 음성 댓글 여부
    voice_choice = models.CharField(max_length=50, default='alloy') # 사용자 음성 선택
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 최신 댓글이 가장 먼저 보이도록 정렬
        ordering = ['created_at'] 

    def __str__(self):
        return f'{self.user.username} - {self.book.title[:10]} 댓글'