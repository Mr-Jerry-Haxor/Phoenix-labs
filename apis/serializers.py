from rest_framework import serializers
from .models import *

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcription
        fields = ('file', 'uploaded_on',)