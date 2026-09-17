import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")

class Config:
    
    API_TOKEN = "1061QKD-H8GMMVA-KCCHRV1-983ZBH2"
    
    
    BASE_URL_UI = "https://www.kinopoisk.ru/"
    BASE_URL_API = "https://api.kinopoisk.dev/v1.4"

