from content_generator import ContentGenerator
from facebook_poster import FacebookPoster
from database import Database
from analytics import SmartScheduler
from trending import TrendingTopics
from engagement import EngagementEngine
from courses import EnglishCourseGenerator
from datetime import datetime, timedelta
import time
import signal
import sys
import random

class UltimateAutoBrain:
    def __init__(self):
        self.content_gen = ContentGenerator()
        self.fb_poster = FacebookPoster()
        self.db = Database()
        self.analytics = SmartScheduler()
        self.trending = TrendingTopics()
        self.engagement = EngagementEngine()
        self.courses = EnglishCourseGenerator()
        
        self.last_post_hour = None
        self.post_count = 0
        self.course_day = 1
        self.course_active = False
        self.current_course = None
        
        # Smart schedule (auto-updated)
        self.schedule = self.analytics.update_schedule()
    
    def refresh_schedule(self):
        """Refresh posting schedule based on analytics"""
        self.schedule = self.analytics.update_schedule()
        print(f"📊 Schedule updated: {len(self.schedule)} optimal times found")
    
    def get_trending_instruction(self, category):
        """Get instruction with trending topics"""
        trends = self.trending.get_trending_english_topics()
        
        instructions = {
            'vocabulary': f"Create a Word of the Day post. Today's trending theme: {random.choice(trends.get('current_trends', ['general']))}. Choose an interesting English word YOURSELF. Write ENTIRELY in English.",
            'grammar': f"Create a grammar tip post. Popular topic area: {random.choice(trends.get('grammar', ['common mistakes']))}. Choose YOUR own grammar topic. Write ENTIRELY in English.",
            'quiz': f"Create an English quiz. Trending: {random.choice(trends.get('current_trends', ['English practice']))}. Pick YOUR own quiz topic. Write ENTIRELY in English.",
            'idiom': f"Create an idiom post. Choose a useful English idiom YOURSELF. Write ENTIRELY in English.",
            'course': f"Create a course post for Day {self.course_day}. Make it engaging and educational. Write ENTIRELY in English.",
            'poll': f"Create an engaging poll about English learning preferences. Write ENTIRELY in English.",
            'engagement': f"Create a fill-in-the-blank English exercise. Make it fun and challenging. Write ENTIRELY in English."
        }
        return instructions.get(category, instructions['vocabulary'])
    
    def decide_post_type(self):
        """Decide what type of post to create"""
        hour = datetime.now().hour
        day_of_week = datetime.now().strftime('%A')
        
        # Special schedules
        if day_of_week == 'Monday' and hour == 6:
            return 'course_intro'
        elif self.course_active and hour == 10:
            return 'course'
        elif hour in [8, 16]:  # High engagement times for polls
            return random.choice(['poll', 'quiz'])
        elif hour < 10:
            return 'vocabulary'
        elif hour < 14:
            return 'grammar'
        elif hour < 18:
            return 'quiz'
        else:
            return 'idiom'
    
    def generate_and_post(self):
        """Main posting function"""
        try:
            post_type = self.decide_post_type()
            
            print(f"\n{'='*50}")
            print(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
            print(f"📝 Post Type: {post_type}")
            
            content = None
            category = post_type
            
            # Handle special post types
            if post_type == 'course_intro':
                self.current_course = '7_day_grammar'
                self.course_active = True
                self.course_day = 1
                content = self.courses.generate_course_intro(self.current_course)
                category = 'course'
                
            elif post_type == 'course':
                if self.current_course:
                    content = self.courses.get_course_post(self.current_course, self.course_day)
                    self.course_day += 1
                    if self.course_day > 7:
                        self.course_active = False
                        self.course_day = 1
                category = 'course'
                
            elif post_type == 'poll':
                content, _ = self.engagement.generate_poll_post()
                category = 'poll'
                
            elif post_type == 'engagement':
                content, _ = self.engagement.generate_fill_in_blank()
                category = 'quiz'
            
            # Standard AI-generated posts
            if not content:
                instruction = self.get_trending_instruction(post_type)
                content = self._ai_generate(instruction)
            
            if not content:
                content = self._emergency_fallback(category)
            
            print(f"✅ Content ready ({len(content)} chars)")
            
            # Post to Facebook
            result = self.fb_poster.post_content(content)
            
            self.db.log_post(
                topic=f"AI-{category}",
                category=category,
                content=content,
                post_id=result.get('post_id'),
                status='success' if result['success'] else 'failed'
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
    
    def _ai_generate(self, instruction):
        """Generate content using AI"""
        headers = {
            "Authorization": f"Bearer {self.content_gen.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.content_gen.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert English teacher creating viral Facebook posts. Choose topics YOURSELF. Be creative, engaging, and educational. Write ENTIRELY in English. Use emojis and hashtags."
                },
                {"role": "user", "content": instruction}
            ],
            "temperature": 0.95,
            "max_tokens": 500
        }
        
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
                    if len(content) > 50:
                        return content
                time.sleep(2)
            except Exception as e:
                print(f"⚠️ AI attempt {attempt+1}: {e}")
                time.sleep(2)
        return None
    
    def _emergency_fallback(self, category):
        """Emergency fallback content"""
        fallbacks = {
            'vocabulary': "📚 Word of the Day: Resilience\n\nThe ability to bounce back from difficulties. 💪\n\nExample: 'Her resilience inspired everyone around her.'\n\nUse it in a sentence! 👇\n\n#WordOfTheDay #LearnEnglish #ESL",
            'grammar': "📖 Grammar Tip: Present Perfect\n\nUse: have/has + past participle\nExample: 'I have learned so much!'\n\nPerfect your English today! 🌟\n\n#GrammarTips #EnglishGrammar",
            'quiz': "🎯 Quick Quiz!\n\nWhich is correct?\nA) I have went\nB) I have gone\n\nComment your answer! 👇\n\n#EnglishQuiz #LearnEnglish",
            'idiom': "💬 Idiom: Break the ice\n\nMeaning: Start a conversation 🗣️\n\nHow do YOU break the ice? Share below!\n\n#IdiomOfTheDay #EnglishIdioms",
            'poll': "📊 Poll: What's hardest in English?\n\n1. Grammar\n2. Vocabulary\n3. Pronunciation\n4. Speaking\n\nVote by commenting! 👇\n\n#Poll #EnglishLearning",
            'course': "📚 Course Day: Keep learning!\n\nEvery day is progress. Stay consistent! 💪\n\n#LearnEnglish #EnglishCourse"
        }
        return fallbacks.get(category, "🌟 Keep learning English! Every day is a new opportunity to improve! 💪\n\n#LearnEnglish #ESL")

def signal_handler(sig, frame):
    print('\n👋 Shutting down...')
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("""
    ╔═══════════════════════════════════════╗
    ║  🚀 ULTIMATE ENGLISH LEARNING BOT    ║
    ║  ⏰ Smart Schedule                   ║
    ║  🔥 Trending Topics                  ║
    ║  🎯 Engagement Quizzes               ║
    ║  📚 Auto Course Series               ║
    ║  🧠 100% AI-Powered                  ║
    ╚═══════════════════════════════════════╝
    """)
    
    brain = UltimateAutoBrain()
    print("🚀 Started!\n")
    
    while True:
        try:
            hour = datetime.now().hour
            minute = datetime.now().minute
            
            should_post = False
            for slot in brain.schedule:
                if slot['hour'] == hour and minute < 15 and hour != brain.last_post_hour:
                    should_post = True
                    break
            
            if should_post:
                print(f"\n⏰ Posting time: {hour}:{minute:02d}")
                brain.generate_and_post()
                time.sleep(3600)
            else:
                if minute % 30 == 0:
                    print(f"⏳ {datetime.now().strftime('%H:%M')} - Waiting... (Posted: {brain.post_count})")
                    # Refresh schedule every 6 hours
                    if hour % 6 == 0 and minute == 0:
                        brain.refresh_schedule()
                time.sleep(60)
                
        except Exception as e:
            print(f"❌ Loop error: {e}")
            time.sleep(60)
