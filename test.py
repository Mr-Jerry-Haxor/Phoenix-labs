from transformers import pipeline

# Create a pipeline for text-to-text generation using the m2m100 model
pipe = pipeline(task='text2text-generation', model='facebook/m2m100_418M')

# Prompt the user for input text and target language
input_text = input("Enter the text you want to translate: ")
target_language = input("Enter the target language (e.g., 'fr' for French): ")

# Translate the input text to the target language
translation = pipe(input_text, forced_bos_token_id=pipe.tokenizer.get_lang_id(lang=target_language))

# Print the translated text
print("Translated text:", translation[0]['generated_text'])
