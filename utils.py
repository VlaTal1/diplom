import PyPDF2
from openai import OpenAI
import re
import math
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from vertexai.generative_models import Part, SafetySetting, GenerativeModel

generation_config = {
    "temperature": 0.0,
    "response_mime_type": "application/json"
}

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE
    ),
]

def read_pdf(file_path: str):
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
            return text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def read_epub(file_path):
    book = epub.read_epub(file_path)
    text_content = []

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_body_content(), 'html.parser')
            text_content.append(soup.get_text())

    text = '\n'.join(text_content)
    return remove_extra_newlines(text)

def gpt_generate_answer(client: OpenAI, prompt: str, model: str):
    chat_completion = client.chat.completions.create(
        model = model,
        response_format={ "type": "json_object" },
        messages = [
            {"role": "user", "content": prompt},
        ],
        temperature = 0.01,
    )

    return chat_completion

def gemini_generate_answer(model: GenerativeModel, prompt: str):
    response = model.generate_content(prompt,
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)

    return response

def split_text_into_parts(text: str, num_parts: int):
    paragraphs = re.split('\n', text.strip())
    
    paragraphs_per_part = math.ceil(len(paragraphs) / (num_parts))
    
    parts = []
    current_part = ""
    
    for i, paragraph in enumerate(paragraphs):
        current_part += paragraph + "\n"
        if (i + 1) % paragraphs_per_part == 0 or (i + 1) == len(paragraphs):
            parts.append(current_part.strip())
            current_part = ""
    
    return parts

def remove_extra_newlines(text):
    return re.sub(r'\n+', '\n', text)