from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import FileUploadSerializer ,TranslationSerializer ,AudioRecognitionSerializer
import wave
import soundfile
import numpy as np
import stt
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
from transformers import pipeline

# Create a pipeline for text-to-text generation using the m2m100 model
pipe = pipeline(task='text2text-generation', model='facebook/m2m100_418M')



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

            # Update the audio file model with the inference result
            audio_file.transcript = text
            audio_file.save()
            # serializer.save(transcript=text)

            return Response({ "transcript": text }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class TranslationView(APIView):
    serializer_class = TranslationSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            input_text = request.data.get('input_text')
            target_language = request.data.get('target_language')
            # Translate the input text to the target language
            
            translation = pipe(input_text, forced_bos_token_id=pipe.tokenizer.get_lang_id(lang=target_language))
            # Return the translated text
            return Response({'translated_text': translation[0]['generated_text']}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class AudioRecognitionView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = FileUploadSerializer
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Get the saved audio file
            audio_instance = serializer.instance
            audio_file = audio_instance.file.path
        

            # Perform speech recognition on the audio file
            try:
                # recognized_text = self.silence_based_conversion(audio_file)
                recognized_text = self.recognize_audio_chunk(audio_file)
                # Update the audio file model with the inference result
                audio_instance.transcript = recognized_text
                audio_instance.save()
                return Response({'recognized_text': recognized_text}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def silence_based_conversion(self, audio_file):
        # Open the audio file stored in the local system as a wav file.
        song = AudioSegment.from_wav(audio_file)

        # Open a file where we will concatenate and store the recognized text
        recognized_text = ""

        # Split track where silence is 0.5 seconds or more and get chunks
        chunks = split_on_silence(song,
            min_silence_len=500,  # Must be silent for at least 0.5 seconds (500 ms)
            silence_thresh=-16  # Consider it silent if quieter than -16 dBFS
        )

        for i, chunk in enumerate(chunks):
            # Create 0.5 seconds silence chunk
            chunk_silent = AudioSegment.silent(duration=10)

            # Add 0.5 sec silence to the beginning and end of audio chunk
            audio_chunk = chunk_silent + chunk + chunk_silent

            # Export audio chunk and save it
            audio_chunk.export(f"./audio_chunks/chunk{i}.wav", bitrate='192k', format="wav")

            # Recognize the chunk
            recognized_chunk = self.recognize_audio_chunk(f"./audio_chunks/chunk{i}.wav")

            if recognized_chunk:
                recognized_text += recognized_chunk + " "

        return recognized_text

    def recognize_audio_chunk(self, audio_chunk_path):
        r = sr.Recognizer()
        try:
            with sr.AudioFile(audio_chunk_path) as source:
                r.adjust_for_ambient_noise(source)
                audio_listened = r.listen(source)
                rec = r.recognize_google(audio_listened)
                return rec
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            raise Exception(f"Speech recognition error: {str(e)}")



















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