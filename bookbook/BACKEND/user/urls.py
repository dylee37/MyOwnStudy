from django.urls import path
from .views import UserSignupView, UserLoginView, AccountDeleteView, UserProfileUpdateView

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('delete/', AccountDeleteView.as_view(), name='account-delete'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile-update'),
]