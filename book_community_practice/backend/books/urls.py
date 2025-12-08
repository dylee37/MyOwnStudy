from rest_framework.routers import DefaultRouter
from .views import BookViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet)  # /books 엔드포인트 등록

urlpatterns = router.urls

