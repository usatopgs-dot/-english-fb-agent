"""Runs once - generates ONE post and publishes to Facebook"""
import requests
import os
from datetime import datetime
import random

# API Keys from environment
API_KEY = os.getenv('GLM_API_KEY')
ENDPOINT = os.getenv('GLM_ENDPOINT', 'https://integrate.api.nvidia.com/v1/chat/completions')
MODEL = os.getenv('GLM_MODEL', 'qwen/qwen3.5-397b-a17b')
FB_PAGE_ID = os.getenv('FB_PAGE_ID')
FB_TOKEN = os.getenv('FB_ACCESS_TOKEN')

def get_category():
    """Determine category based on time"""
    hour = datetime.utcnow().hour
    
    # Convert UTC to IST (UTC+5:30)
    ist_hour = (hour + 5) % 24
    ist_hour += 0.5 if datetime.utcnow().minute >= 30 else 0
    
    if 5 <= ist_hour < 9:
        return 'vocabulary', "Create a Word of the Day post. Choose an interesting word YOURSELF."
    elif 9 <= ist_hour < 13:
        return 'grammar', "Create a grammar tip post. Choose a grammar topic YOURSELF."
    elif 13 <= ist_hour < 17:
        return 'quiz', "Create an English quiz post. Choose a quiz topic YOURSELF."
    elif 17 <= ist_hour < 21:
        return 'idiom', "Create an idiom post. Choose a useful idiom YOURSELF."
    else:
        return 'vocabulary', "Create a Word of the Day post."

def generate_post(category, instruction):
    """Generate post using AI"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are an expert English teacher creating Facebook posts. Choose topics YOURSELF. Write ENTIRELY in English. Use emojis, line breaks, and hashtags."
            },
            {"role": "user", "content": instruction}
        ],
        "temperature": 0.95,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(ENDPOINT, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"AI Error: {e}")
    
    # Fallback
    fallbacks = {
        'vocabulary': "📚 Word of the Day: Resilience\n\nThe ability to bounce back from difficulties. 💪\n\n#WordOfTheDay #LearnEnglish",
        'grammar': "📖 Grammar Tip: Present Perfect\n\nUse: have/has + past participle\n\n#GrammarTips #EnglishGrammar",
        'quiz': "🎯 Quick Quiz!\n\nWhich is correct?\nA) I have gone\nB) I have went\n\n#EnglishQuiz",
        'idiom': "💬 Idiom: Break the ice\n\nMeaning: Start a conversation 🗣️\n\n#IdiomOfTheDay"
    }
    return fallbacks.get(category, "🌟 Keep learning English! 💪\n\n#LearnEnglish")

def post_to_facebook(content):
    """Post to Facebook page"""
    try:
        import facebook
        graph = facebook.GraphAPI(access_token=FB_TOKEN)
        result = graph.put_object(
            parent_object=FB_PAGE_ID,
            connection_name='feed',
            message=content
        )
        print(f"✅ Posted! ID: {result['id']}")
        return result['id']
    except Exception as e:
        print(f"❌ Facebook Error: {e}")
        return None

def main():
    print(f"🕐 Starting at: {datetime.utcnow()} UTC")
    
    category, instruction = get_category()
    print(f"📂 Category: {category}")
    
    print("🧠 Generating post...")
    content = generate_post(category, instruction)
    
    print(f"✅ Generated ({len(content)} chars)")
    print(f"📝 Preview: {content[:100]}...")
    
    print("📤 Posting to Facebook...")
    post_id = post_to_facebook(content)
    
    if post_id:
        print(f"🎉 Success! Post ID: {post_id}")
    else:
        print("❌ Failed to post")

if __name__ == '__main__':
    main()
