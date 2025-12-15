from django.contrib import admin
from django.urls import path, include
from user.views import CustomTokenObtainPairView # ⭐️ 커스텀 뷰 import
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/user/', include('user.urls')),
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # 기존 라인 주석 처리 또는 삭제
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'), # ⭐️ 커스텀 뷰로 교체
    path('api/', include('books.urls')), # ⭐️ books 앱의 URL 포함
    
]
