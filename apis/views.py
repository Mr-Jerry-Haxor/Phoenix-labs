from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import FileUploadSerializer, ScrapedDataSerializer ,TranslationSerializer 
from rest_framework import generics
# Audio transcribe code.
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


import requests
from bs4 import BeautifulSoup
from autoscraper import AutoScraper



# Create a pipeline for text-to-text generation using the m2m100 model
translatepipe = pipeline(task='text2text-generation', model='facebook/m2m100_418M')



class TranslationView(APIView):
    serializer_class = TranslationSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            input_text = request.data.get('input_text')
            target_language = request.data.get('target_language')
            # Translate the input text to the target language
            
            translation = translatepipe(input_text, forced_bos_token_id=translatepipe.tokenizer.get_lang_id(lang=target_language))
            # Return the translated text
            return Response({'translated_text': translation[0]['generated_text']}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#audio transcription api

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = "openai/whisper-large-v3"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)
model = model.to_bettertransformer()
processor = AutoProcessor.from_pretrained(model_id)

audiopipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    chunk_length_s=30,
    batch_size=16,
    return_timestamps=True,
    torch_dtype=torch_dtype,
    device=device,
)

class AudioRecognitionView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = FileUploadSerializer
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            audio_instance = serializer.instance
            audio_file = audio_instance.file.path
        
            try:
                # recognized_text = self.silence_based_conversion(audio_file)
                recognized_text = audiopipe(audio_file)
                # Update the audio file model with the inference result
                audio_instance.transcript = recognized_text["text"]
                audio_instance.save()
                return Response({'recognized_text': recognized_text["text"]}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



def scrape_data_from_tag(url, tag):
    # Send a GET request to the URL and retrieve the HTML content
    response = requests.get(url)
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all the elements with the provided tag
        elements = soup.find_all(tag)
        
        # Extract the text content from the elements
        if tag == "img":
            data = [element['src'] for element in elements]
        else:
            data = [element.get_text() for element in elements]
        
        return data
    else:
        print(f"Failed to fetch data from {url}. Error code: {response.status_code}")
        return []


def scrape_data_from_wanted_list(url, wanted_list):
    scraper = AutoScraper()
    result = scraper.build(url, wanted_list)
    return result



class ScrapeDataAPIView(generics.CreateAPIView):
    serializer_class = ScrapedDataSerializer

    def create(self, request, *args, **kwargs):
        user_url = request.data.get('url')
        user_input = str(request.data.get('data'))

        if user_input[0] == "<" and user_input[-1] == ">":
            user_tag = user_input.lower() 
            user_tag = user_tag[1:-1]
            scraped_data = scrape_data_from_tag(user_url, user_tag)
        else:
            user_wanted_text = [user_input]
            scraped_data = scrape_data_from_wanted_list(user_url, user_wanted_text)
        if scraped_data:
            data = {
                'url': user_url,
                'data': '\n'.join(scraped_data)
            }
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({"scraped data" :  data}, status=status.HTTP_201_CREATED)
        else:
            return Response("No data found.", status=status.HTTP_404_NOT_FOUND)