from rest_framework import serializers
from .models import *

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcription
        fields = ('file', 'uploaded_on',)
        
        
class TranslationSerializer(serializers.Serializer):
    input_text = serializers.CharField()
    target_language = serializers.CharField()
    
    
class ScrapedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapedData
        fields = '__all__'