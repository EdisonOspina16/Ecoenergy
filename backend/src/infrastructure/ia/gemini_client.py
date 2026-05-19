from google import genai
from src.config import GEMINI_API_KEY, GEMINI_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)
MODELO = GEMINI_MODEL
