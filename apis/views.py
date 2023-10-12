from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import FileUploadSerializer
import wave
import soundfile
import numpy as np
import stt
model_file_path = 'Datafiles\deepspeech-0.9.3-models.tflite'
model = stt.Model(model_file_path)
scorer_file_path = 'Datafiles\deepspeech-0.9.3-models.scorer'
model.enableExternalScorer(scorer_file_path)
lm_alpha = 0.75
lm_beta = 1.85
model.setScorerAlphaBeta(lm_alpha, lm_beta)
beam_width = 500
model.setBeamWidth(beam_width)

# Your Django view function
class FileUploadAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Get the saved audio file
            audio_file = serializer.instance
            audio_path = audio_file.file.path

            data, samplerate = soundfile.read(audio_path)
            soundfile.write(audio_path, data, samplerate)
            
            w = wave.open(audio_path, 'r')
            rate = w.getframerate()
            frames = w.getnframes()
            buffer = w.readframes(frames)

            data16 = np.frombuffer(buffer, dtype=np.int16)
            text = model.stt(data16)
            print(text)

            # Update the audio file model with the inference result
            audio_file.transcript = text
            audio_file.save()
            # serializer.save(transcript=text)

            return Response({ "transcript": text }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

























# class FileUploadAPIView(APIView):
#     parser_classes = (MultiPartParser, FormParser)
#     serializer_class = FileUploadSerializer
    
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             # you can access the file like this from serializer
#             # uploaded_file = serializer.validated_data["file"]
#             serializer.save()
#             return Response(
#                 serializer.data,
#                 status=status.HTTP_201_CREATED
#             )
        
#         return Response(
#             serializer.errors,
#             status=status.HTTP_400_BAD_REQUEST
#         )