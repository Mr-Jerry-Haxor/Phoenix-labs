from django.urls import path
from .views import FileUploadAPIView, TranslationView ,AudioRecognitionView
# from rest_framework.routers import DefaultRouter
#
# router = DefaultRouter()
# router.register('upload-file', FileUploadAPIView, basename='upload-file')
# router.register('upload-image', ImageUploadAPIView, basename='upload-image')
#
# urlpatterns = router.urls
#
# urlpatterns += [
#     path('upload-file/', FileUploadAPIView.as_view(), name='upload-file'),
#     path('upload-image/', ImageUploadAPIView.as_view(), name='upload-image'),
# ]

urlpatterns = [
    path('transcript/', FileUploadAPIView.as_view(), name='transcript'),
    path('translate/', TranslationView.as_view(), name='translate'),
    path('transcript-v2/', AudioRecognitionView.as_view(), name='recognize-audio'),
]
