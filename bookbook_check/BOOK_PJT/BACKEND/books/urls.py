from django.urls import path
from .views import (BookListView, BookDetailView, RecommendedBooksView, 
                    BestsellerListView, RecommendationView, CommentCreateView,
                    CommentDestroyView, TextToSpeechView)

urlpatterns = [
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('books/<int:book_pk>/comments/', CommentCreateView.as_view(), name='book-comment-create'),
    path('books/recommendations/<int:pk>/', RecommendedBooksView.as_view(), name='book-recommendations'), 
    path('books/<int:book_pk>/comments/<int:pk>/', CommentDestroyView.as_view(), name='book-comment-destroy'),
    path('books/bestsellers/', BestsellerListView.as_view(), name='book-bestsellers'),
    path('books/main-recommendations/', RecommendationView.as_view(), name='main-recommendation'),
    path('books/tts/', TextToSpeechView.as_view(), name='text-to-speech'),
]