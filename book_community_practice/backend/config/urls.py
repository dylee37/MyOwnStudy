from django.contrib import admin
from django.urls import path, include
from books.urls import router

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),  # 모든 books API는 /api/books로 접근
]
