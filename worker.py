from content_generator import ContentGenerator
from facebook_poster import FacebookPoster
from database import Database
from datetime import datetime
import time
import signal
import sys

class SmartAutoBrain:
    def __init__(self):
        self.content_gen = ContentGenerator()
        self.fb_poster = FacebookPoster()
        self.db = Database()
        self.last_post_hour = None
        self.post_count = 0
    
    def generate_and_post(self):
        """AI khud topic sochega, post banayega, publish karega - ek hi call vich"""
        try:
            hour = datetime.now().hour
            
            # Time ke hisaab se category set
            if 6 <= hour < 10:
                category = 'vocabulary'
                instruction = "Create a Word of the Day post. Choose an interesting English word YOURSELF. Include: pronunciation, meaning, 2 examples, memory tip, engagement question, and 5-7 hashtags. Write ENTIRELY in English."
            elif 10 <= hour < 14:
                category = 'grammar'
                instruction = "Create a grammar tip post. Choose a grammar topic YOURSELF that learners find confusing. Include: simple explanation, 2 correct examples, 1 common mistake, practice question, and 5-7 hashtags. Write ENTIRELY in English."
            elif 14 <= hour < 18:
                category = 'quiz'
                instruction = "Create an English quiz post. Choose a quiz topic YOURSELF. Include: question, 4 options (A-D), hint, ask for comments, and 5-7 hashtags. Write ENTIRELY in English."
            elif 18 <= hour < 22:
                category = 'idiom'
                instruction = "Create an idiom post. Choose a useful English idiom YOURSELF. Include: idiom, meaning, 2 examples, origin fun fact, challenge for followers, and 5-7 hashtags. Write ENTIRELY in English."
            else:
                category = 'vocabulary'
                instruction = "Create a Word of the Day post. Choose an interesting English word YOURSELF. Include: pronunciation, meaning, examples, and hashtags. Write ENTIRELY in English."
            
            print(f"\n{'='*50}")
            print(f"🕐 {datetime.now().strftime('%H:%M:%S')} | 📂 {category}")
            print(f"🧠 AI choosing topic & generating post...")
            
            # Single API call - AI does everything
            headers = {
                "Authorization": f"Bearer {self.content_gen.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.content_gen.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert English teacher creating Facebook posts. Choose topics YOURSELF. Be creative, original, and never repeat. Write ENTIRELY in English. Use emojis, line breaks, and end with a question."
                    },
                    {
                        "role": "user",
                        "content": instruction
                    }
                ],
                "temperature": 0.95,
                "max_tokens": 500,
                "top_p": 0.9
            }
            
            # 3 retry attempts
            content = None
            for attempt in range(3):
                try:
                    import requests
                    response = requests.post(
                        self.content_gen.endpoint,
                        headers=headers,
                        json=payload,
                        timeout=25
                    )
                    if response.status_code == 200:
                        result = response.json()
                        content = result['choices'][0]['message']['content']
                        if len(content) > 50 and '#' in content:
                            break
                    print(f"   ⚠️ Attempt {attempt+1} failed")
                    time.sleep(2)
                except Exception as e:
                    print(f"   ⚠️ Attempt {attempt+1}: {e}")
                    time.sleep(2)
            
            if not content:
                # Emergency fallback
                content = f"""📚 English Learning Tip

Let's improve our English together! 🌟

Practice makes perfect - what are you learning today?

💬 Share your current English learning goal in the comments!

#LearnEnglish #EnglishTips #DailyEnglish #{category}"""
                print("   🔄 Using emergency fallback")
            
            print(f"✅ Generated ({len(content)} chars)")
            
            # Post to Facebook
            result = self.fb_poster.post_content(content)
            
            # Log to database
            self.db.log_post(
                topic=f"AI-{category}",
                category=category,
                content=content,
                post_id=result.get('post_id'),
                status='success' if result['success'] else 'failed',
                error=result.get('error')
            )
            
            if result['success']:
                print(f"🎉 Posted! ID: {result['post_id']}")
                self.last_post_hour = datetime.now().hour
                self.post_count += 1
            else:
                print(f"❌ Failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {'success': False, 'error': str(e)}

def signal_handler(sig, frame):
    print('\n👋 Shutting down...')
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("""
    ╔══════════════════════════════════╗
    ║  📚 ENGLISH LEARNING AUTO BOT   ║
    ║  🧠 100% AI-Generated Topics    ║
    ║  ⏰ Posts: 6AM 10AM 2PM 6PM    ║
    ║  🔄 Auto-Retry if fails         ║
    ╚══════════════════════════════════╝
    """)
    
    brain = SmartAutoBrain()
    print("🚀 Started! Waiting for posting times...\n")
    
    while True:
        try:
            hour = datetime.now().hour
            minute = datetime.now().minute
            
            # Post at 6, 10, 14, 18 hours
            posting_hours = [6, 10, 14, 18]
            
            if hour in posting_hours and hour != brain.last_post_hour and minute < 15:
                print(f"\n⏰ Posting time: {hour}:{minute:02d}")
                brain.generate_and_post()
                time.sleep(3600)  # Sleep 1 hour after posting
            else:
                # Status every 10 minutes
                if minute % 10 == 0:
                    print(f"⏳ {datetime.now().strftime('%H:%M')} - Waiting... (Posted today: {brain.post_count})")
                time.sleep(60)
                
        except Exception as e:
            print(f"❌ Loop error: {e}")
            time.sleep(60)
