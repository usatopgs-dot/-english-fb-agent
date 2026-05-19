import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # GLM-5.1 Settings
    GLM_API_KEY = os.getenv('GLM_API_KEY')
    GLM_ENDPOINT = os.getenv('GLM_ENDPOINT', 'https://integrate.api.nvidia.com/v1/chat/completions')
    GLM_MODEL = os.getenv('GLM_MODEL', 'z-ai/glm-5.1')
    
    # Facebook Settings
    FB_PAGE_ID = os.getenv('FB_PAGE_ID')
    FB_ACCESS_TOKEN = os.getenv('FB_ACCESS_TOKEN')
    
    # App Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Posting Schedule (IST - Indian Time)
    POST_SCHEDULE = {
        'word_of_day': {'hour': 9, 'minute': 0},      # 9:00 AM
        'grammar_tip': {'hour': 13, 'minute': 0},      # 1:00 PM
        'quiz_time': {'hour': 17, 'minute': 0},         # 5:00 PM
        'idiom_post': {'hour': 20, 'minute': 0},        # 8:00 PM
    }
