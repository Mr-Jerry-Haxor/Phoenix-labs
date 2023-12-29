from django.urls import path
from .views import  *


urlpatterns = [
    path('translate/', TranslationView.as_view(), name='translate'),
    path('transcript/', AudioRecognitionView.as_view(), name='recognize-audio'),
    path('scrape/', ScrapeDataAPIView.as_view(), name='scrape-data'),
]
