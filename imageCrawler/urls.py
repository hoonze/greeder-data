from django.urls import path
from django.urls import path, include
from .views import ImageViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# 첫 번째 인자는 url의 prefix
# 두 번째 인자는 ViewSet
router.register('image', ImageViewSet)

urlpatterns = [
    path('', include(router.urls))
]
