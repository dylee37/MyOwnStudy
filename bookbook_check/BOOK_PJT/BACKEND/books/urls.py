from django.urls import path
from .views import (BookListView, BookDetailView, RecommendedBooksView, 
                    BestsellerListView, PersonalizedRecommendationView, CommentCreateView,
                    CommentDestroyView)

urlpatterns = [
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('books/<int:book_pk>/comments/', CommentCreateView.as_view(), name='book-comment-create'),
    path('books/recommendations/<int:pk>/', RecommendedBooksView.as_view(), name='book-recommendations'), 
    path('books/<int:book_pk>/comments/<int:pk>/', CommentDestroyView.as_view(), name='book-comment-destroy'),
    path('books/bestsellers/', BestsellerListView.as_view(), name='book-bestsellers'),
    path('books/personalized-recommendation/', PersonalizedRecommendationView.as_view(), name='personalized-recommendation'),
]