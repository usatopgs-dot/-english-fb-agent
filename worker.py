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
        self.post_count_today = 0
        self.daily_limit = 4
        self.course_day = 1
        self.course_active = False
        self.current_course = None
        self.consecutive_errors = 0
        self.max_errors = 5
        
        # Default schedule (used until analytics has data)
        self.schedule = self._get_default_schedule()
        self._refresh_schedule_if_needed()
    
    def _get_default_schedule(self):
        """Default posting schedule based on research"""
        return [
            {'hour': 6, 'minute': 0, 'label': '🌅 Morning Word'},
            {'hour': 10, 'minute': 0, 'label': '☀️ Grammar Tip'},
            {'hour': 14, 'minute': 0, 'label': '🌤️ Quiz Time'},
            {'hour': 18, 'minute': 0, 'label': '🌙 Idiom Post'}
        ]
    
    def _refresh_schedule_if_needed(self):
        """Refresh schedule from analytics every 6 hours"""
        current_hour = datetime.now().hour
        if current_hour % 6 == 0:
            try:
                new_schedule = self.analytics.update_schedule()
                if new_schedule and len(new_schedule) >= 3:
                    self.schedule = new_schedule
                    print(f"📊 Schedule updated from analytics: {len(self.schedule)} times")
                else:
                    self.schedule = self._get_default_schedule()
                    print("📊 Using default schedule (not enough analytics data yet)")
            except Exception as e:
                print(f"⚠️ Analytics refresh failed: {e}, using default schedule")
                self.schedule = self._get_default_schedule()
    
    def decide_post_type(self):
        """Smart decision: what type of post to create"""
        hour = datetime.now().hour
        day_of_week = datetime.now().strftime('%A')
        day_of_month = datetime.now().day
        
        # Monday 6AM: Start new course
        if day_of_week == 'Monday' and hour == 6 and day_of_month % 7 <= 1:
            return 'course_intro'
        
        # Course active: continue daily course
        if self.course_active and hour == 10:
            return 'course'
        
        # High engagement times: polls and quizzes
        if hour in [8, 12, 16, 20]:
            poll_chance = random.random()
            if poll_chance < 0.3:
                return 'poll'
            elif poll_chance < 0.5:
                return 'engagement'
        
        # Standard time-based categories
        if 5 <= hour < 9:
            return 'vocabulary'
        elif 9 <= hour < 13:
            return 'grammar'
        elif 13 <= hour < 17:
            return 'quiz'
        elif 17 <= hour < 21:
            return 'idiom'
        else:
            return 'vocabulary'
    
    def get_ai_instruction(self, post_type):
        """Get AI instruction with trending topics"""
        try:
            trends = self.trending.get_trending_english_topics()
            trending_theme = random.choice(trends.get('current_trends', ['general English']))
        except:
            trending_theme = "general English learning"
        
        instructions = {
            'vocabulary': f"Create a Word of the Day post. Today's theme: {trending_theme}. Choose an interesting English word YOURSELF. Include: pronunciation, meaning, 2 examples, memory tip, question, 5-7 hashtags. Write ENTIRELY in English. Be original!",
            
            'grammar': f"Create a grammar tip post. Popular topic: {random.choice(trends.get('grammar', ['common mistakes'])) if 'trends' in dir() else 'common grammar mistakes'}. Choose YOUR own grammar topic. Include: rule, 2 examples, 1 mistake, practice question, 5-7 hashtags. Write ENTIRELY in English.",
            
            'quiz': f"Create an English quiz post. Theme: {trending_theme}. Pick YOUR own quiz topic. Include: question, 4 options (A-D), hint, ask for comments, 5-7 hashtags. Write ENTIRELY in English.",
            
            'idiom': f"Create an idiom post. Choose a useful English idiom YOURSELF. Include: idiom, meaning, 2 examples, fun fact, challenge, 5-7 hashtags. Write ENTIRELY in English.",
            
            'course': f"Create a course post for Day {self.course_day} of the 7-Day Grammar Masterclass. Today's topic: {['Present Tenses', 'Past Tenses', 'Future Forms', 'Conditionals', 'Passive Voice', 'Reported Speech', 'Review & Quiz'][min(self.course_day-1, 6)]}. Write ENTIRELY in English.",
            
            'poll': f"Create an engaging English learning poll. Ask about learning preferences or difficulties. Give 4 options. Write ENTIRELY in English.",
            
            'engagement': f"Create a fill-in-the-blank English exercise. Make it fun and challenging for intermediate learners. Write ENTIRELY in English."
        }
        
        return instructions.get(post_type, instructions['vocabulary'])
    
    def generate_content(self, post_type):
        """Generate content using AI with retry logic"""
        instruction = self.get_ai_instruction(post_type)
        
        # Special post types that don't need AI
        if post_type == 'course_intro':
            courses_to_try = ['7_day_grammar', '5_day_idioms']
            self.current_course = random.choice(courses_to_try)
            self.course_active = True
            self.course_day = 1
            content = self.courses.generate_course_intro(self.current_course)
            if content:
                return content, 'course'
        
        elif post_type == 'course':
            if self.current_course and self.course_active:
                content = self.courses.get_course_post(self.current_course, self.course_day)
                if content:
                    self.db.log_course_day(self.current_course, self.course_day, f"Day {self.course_day}")
                    self.course_day += 1
                    if self.course_day > 7:
                        self.course_active = False
                        self.course_day = 1
                    return content, 'course'
        
        elif post_type == 'poll':
            content, _ = self.engagement.generate_poll_post()
            if content:
                return content, 'poll'
        
        elif post_type == 'engagement':
            content, _ = self.engagement.generate_fill_in_blank()
            if content:
                return content, 'quiz'
        
        # AI-generated content with retry
        headers = {
            "Authorization": f"Bearer {self.content_gen.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.content_gen.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert English teacher creating viral Facebook posts. Choose topics YOURSELF. Be creative, original, and never repeat. Write ENTIRELY in English. Use emojis, line breaks, and end with a question. Add 5-7 relevant hashtags."
                },
                {"role": "user", "content": instruction}
            ],
            "temperature": 0.95,
            "max_tokens": 500,
            "top_p": 0.9
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
                    if len(content) > 50 and '#' in content:
                        return content, post_type
                print(f"   ⚠️ Attempt {attempt+1}: Status {response.status_code}")
                time.sleep(2)
            except Exception as e:
                print(f"   ⚠️ Attempt {attempt+1}: {str(e)[:50]}")
                time.sleep(2)
        
        return None, post_type
    
    def _get_fallback(self, post_type):
        """Emergency fallback posts"""
        fallbacks = {
            'vocabulary': "📚 Word of the Day: Resilience\n\nThe ability to bounce back from difficulties. 💪\n\nExample: 'Her resilience inspired everyone around her.'\n\nUse it in a sentence! 👇\n\n#WordOfTheDay #LearnEnglish #ESL #Vocabulary #EnglishLearning",
            
            'grammar': "📖 Grammar Tip: Present Perfect\n\nUse: have/has + past participle\nExample: 'I have learned so much!'\n\nWhen: Past actions with present relevance.\n\nPerfect your English today! 🌟\n\n#GrammarTips #EnglishGrammar #LearnEnglish #ESL",
            
            'quiz': "🎯 Quick English Quiz!\n\nWhich is correct?\nA) I have went there\nB) I have gone there\n\nDrop your answer! 👇\n\n#EnglishQuiz #LearnEnglish #ESL",
            
            'idiom': "💬 Idiom: Break the ice\n\nMeaning: Start a conversation 🗣️\n\nExample: 'The game helped break the ice at the party.'\n\nHow do YOU break the ice? Share below!\n\n#IdiomOfTheDay #EnglishIdioms #LearnEnglish",
            
            'poll': "📊 Quick Poll!\n\nWhat's hardest in English?\n1️⃣ Grammar\n2️⃣ Vocabulary\n3️⃣ Pronunciation\n4️⃣ Speaking\n\nVote by commenting! 👇\n\n#Poll #EnglishLearning #ESL",
            
            'engagement': "✍️ Fill in the blank:\n\nShe ___ (go) to school every day.\n\nHint: Present Simple, 3rd person singular\n\nComment your answer! 👇\n\n#EnglishPractice #Grammar #LearnEnglish",
            
            'course': "📚 Course Update: Keep going! You're making progress every day! 💪\n\nPractice makes perfect - what did you learn today?\n\n#EnglishCourse #LearnEnglish #Progress"
        }
        return fallbacks.get(post_type, "🌟 Keep learning English! Every day is a new opportunity! 💪\n\n#LearnEnglish #ESL #DailyEnglish")
    
    def generate_and_post(self):
        """Main function: generate content and post to Facebook"""
        try:
            post_type = self.decide_post_type()
            
            print(f"\n{'='*50}")
            print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📝 Post Type: {post_type}")
            
            # Generate content
            content, actual_category = self.generate_content(post_type)
            
            if not content:
                print("🔄 Using fallback content...")
                content = self._get_fallback(post_type)
                actual_category = post_type
            
            print(f"✅ Content ready ({len(content)} chars)")
            
            # Post to Facebook
            result = self.fb_poster.post_content(content)
            
            # Log to database
            self.db.log_post(
                topic=f"AI-{actual_category}",
                category=actual_category,
                content=content,
                post_id=result.get('post_id'),
                status='success' if result['success'] else 'failed',
                error=result.get('error')
            )
            
            if result['success']:
                print(f"🎉 Posted! ID: {result['post_id']}")
                self.last_post_hour = datetime.now().hour
                self.post_count_today += 1
                self.consecutive_errors = 0
            else:
                print(f"❌ Post failed: {result.get('error')}")
                self.consecutive_errors += 1
            
            return result
            
        except Exception as e:
            print(f"❌ Critical error: {e}")
            self.consecutive_errors += 1
            return {'success': False, 'error': str(e)}
    
    def should_post_now(self):
        """Check if it's time to post"""
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        
        # Daily limit check
        if self.post_count_today >= self.daily_limit:
            return False
        
        # Already posted this hour?
        if self.last_post_hour == current_hour:
            return False
        
        # Error cooldown
        if self.consecutive_errors >= self.max_errors:
            if current_minute % 30 != 0:  # Retry every 30 min
                return False
        
        # Check schedule
        for slot in self.schedule:
            if slot['hour'] == current_hour:
                # Post within first 10 minutes of the hour
                if current_minute < 10:
                    return True
        
        return False
    
    def reset_daily_counter(self):
        """Reset counter at midnight"""
        now = datetime.now()
        if now.hour == 0 and now.minute < 5:
            if self.post_count_today > 0:
                print(f"\n🔄 New day! Yesterday's posts: {self.post_count_today}")
            self.post_count_today = 0
            self.consecutive_errors = 0
            self._refresh_schedule_if_needed()

def signal_handler(sig, frame):
    print('\n\n👋 Shutting down gracefully...')
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
    ║  🔄 Auto-Retry on Errors             ║
    ╚═══════════════════════════════════════╝
    """)
    
    brain = UltimateAutoBrain()
    
    print(f"📅 Schedule: {len(brain.schedule)} posts/day")
    for slot in brain.schedule:
        print(f"   {slot['label']} at {slot['hour']:02d}:{slot['minute']:02d}")
    print(f"\n🚀 Bot started! Waiting for posting times...\n")
    
    while True:
        try:
            brain.reset_daily_counter()
            
            if brain.should_post_now():
                now = datetime.now()
                print(f"\n⏰ Time to post! ({now.strftime('%H:%M')})")
                brain.generate_and_post()
                # Sleep 1 hour after successful post
                time.sleep(3600)
            else:
                # Status update every 15 minutes
                now = datetime.now()
                if now.minute % 15 == 0:
                    print(f"⏳ {now.strftime('%H:%M')} - Waiting... (Posted today: {brain.post_count_today}/{brain.daily_limit})")
                    if brain.consecutive_errors > 0:
                        print(f"   ⚠️ Consecutive errors: {brain.consecutive_errors}")
                time.sleep(60)
                
        except Exception as e:
            print(f"❌ Loop error: {e}")
            time.sleep(60)
