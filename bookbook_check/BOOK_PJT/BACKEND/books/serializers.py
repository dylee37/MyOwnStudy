from rest_framework import serializers
from .models import Book, Category, Comment
from django.db.models import Avg, Count

# ----------------------- 1. Category Serializer -----------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')

# ----------------------- 2. Comment Serializer -----------------------
class CommentSerializer(serializers.ModelSerializer):
    # ReadOnlyField를 사용하여 조회 시 사용자 이름을 보여줍니다.
    user_name = serializers.ReadOnlyField(source='user.name')
    user_id = serializers.ReadOnlyField(source='user.id')
    
    class Meta:
        model = Comment
        # rating 필드는 이제 5점 만점 정수/소수점을 저장합니다.
        fields = ['id', 'user_id', 'user_name', 'content', 'rating', 'is_voice', 'created_at']
        read_only_fields = ['user_id', 'user_name', 'created_at', 'id']


# ----------------------- 3. Book List Serializer -----------------------
class BookListSerializer(serializers.ModelSerializer):
    # rating은 5점 만점 평균 (소수점 포함)
    rating = serializers.SerializerMethodField()
    commentCount = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Book
        fields = (
            'id', 'title', 'author', 'cover', 'rating', 'commentCount', 
            'category_name', 'subTitle', 'publisher', 'pub_date', 'isbn'
        )

    # ⭐️ 메서드 1: 실제 댓글 개수 계산 ⭐️
    def get_commentCount(self, obj):
        return obj.comments.count()

    # ⭐️ 메서드 2: 실제 평점 평균 계산 (5점 만점 기준) ⭐️
    def get_rating(self, obj):
        avg_rating = obj.comments.aggregate(avg_rating=Avg('rating'))['avg_rating']

        if avg_rating is None:
            return 0.0 # 댓글이 없으면 0점 반환

        # 5점 만점 기준으로 통일했으므로 * 2를 제거합니다.
        return round(avg_rating, 1) # 소수점 첫째 자리까지 반올림하여 5점 만점 평점을 반환

# ----------------------- 4. Book Detail Serializer -----------------------
class BookDetailSerializer(BookListSerializer):
    # BookListSerializer 상속 후 상세 필드 추가
    description = serializers.CharField(read_only=True)
    author_info = serializers.CharField(read_only=True)
    author_photo = serializers.URLField(read_only=True)
    
    # ⭐️ TOKTOK (댓글) 목록을 반환합니다. ⭐️
    comments = serializers.SerializerMethodField()

    class Meta(BookListSerializer.Meta):
        fields = BookListSerializer.Meta.fields + (
            'description', 'author_info', 'author_photo', 'comments', 'customer_review_rank'
        )
    
    # ⭐️⭐️ get_comments: 실제 댓글 목록(배열)을 반환하여 상세 페이지 오류 해결 ⭐️⭐️
    def get_comments(self, obj):
        # 해당 책의 모든 댓글을 가져와 최신순으로 정렬 (예시)
        comments = obj.comments.all().order_by('-created_at')
        
        # CommentSerializer를 사용하여 댓글 객체 목록을 직렬화하여 반환
        return CommentSerializer(comments, many=True).data