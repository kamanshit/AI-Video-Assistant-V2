from rest_framework.routers import DefaultRouter
from .views import VideoViewSet, RegisterAPIView, LoginAPIView
from django.urls import path

router = DefaultRouter()
router.register('videos', VideoViewSet, basename='video')

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login')
]

urlpatterns += router.urls
