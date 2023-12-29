
from django.db import models

# Create your models here.
class Transcription(models.Model):
    file = models.FileField()
    uploaded_on = models.DateTimeField(auto_now_add=True)
    transcript = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.uploaded_on.date()
    
class ScrapedData(models.Model):
    url = models.URLField()
    data = models.TextField()