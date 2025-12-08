from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from .models import Book
from .serializers import BookSerializer

# ViewSet을 사용해 CRUD 기능 쉽게 구현
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by('-created_at')  # 최신 글이 먼저 오게 정렬
    serializer_class = BookSerializer

    filter_backends = [SearchFilter]

    search_fields = ['title', 'author']