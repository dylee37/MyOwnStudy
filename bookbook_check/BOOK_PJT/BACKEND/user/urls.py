from django.urls import path
from .views import UserSignupView, UserLoginView, PersonalizedRecommendationView
from . import views

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('me/', views.user_me, name='user_me'),
    path('library/', views.user_library, name='user_library'),
    path('delete/', views.delete_account, name='delete_account'),
    path('recommendation/personalized/', PersonalizedRecommendationView.as_view(), name='personalized_recommendation'),
]