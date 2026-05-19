from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz
from content_generator import ContentGenerator
from facebook_poster import FacebookPoster
from database import Database
from config import Config

class PostScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler(
            timezone=pytz.timezone('Asia/Kolkata')
        )
        self.content_gen = ContentGenerator()
        self.fb_poster = FacebookPoster()
        self.db = Database()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """Setup all scheduled jobs"""
        
        # 9:00 AM - Word of the Day
        self.scheduler.add_job(
            func=self._post_word_of_day,
            trigger=CronTrigger(hour=9, minute=0),
            id='word_of_day',
            name='Daily Word Post'
        )
        
        # 1:00 PM - Grammar Tip
        self.scheduler.add_job(
            func=self._post_grammar_tip,
            trigger=CronTrigger(hour=13, minute=0),
            id='grammar_tip',
            name='Daily Grammar Tip'
        )
        
        # 5:00 PM - Quiz Time
        self.scheduler.add_job(
            func=self._post_quiz,
            trigger=CronTrigger(hour=17, minute=0),
            id='quiz_time',
            name='Daily Quiz'
        )
        
        # 8:00 PM - Idiom Post
        self.scheduler.add_job(
            func=self._post_idiom,
            trigger=CronTrigger(hour=20, minute=0),
            id='idiom_post',
            name='Daily Idiom'
        )
        
        print("✅ All jobs scheduled!")
    
    def _post_word_of_day(self):
        """Post vocabulary content"""
        topics = ['Ephemeral', 'Resilient', 'Serendipity', 'Eloquent', 'Ubiquitous']
        topic = topics[datetime.now().day % len(topics)]
        
        content = self.content_gen.generate_post(topic, 'vocabulary')
        result = self.fb_poster.post_content(content)
        
        self.db.log_post(
            topic=topic,
            category='vocabulary',
            content=content,
            post_id=result.get('post_id'),
            status='success' if result['success'] else 'failed',
            error=result.get('error')
        )
        
        print(f"📚 Word of Day posted: {topic}")
    
    def _post_grammar_tip(self):
        """Post grammar content"""
        topics = ['Past Perfect Tense', 'Conditional Sentences', 
                  'Phrasal Verbs', 'Prepositions', 'Articles A/An/The']
        topic = topics[datetime.now().day % len(topics)]
        
        content = self.content_gen.generate_post(topic, 'grammar')
        result = self.fb_poster.post_content(content)
        
        self.db.log_post(
            topic=topic,
            category='grammar',
            content=content,
            post_id=result.get('post_id'),
            status='success' if result['success'] else 'failed'
        )
        
        print(f"📖 Grammar Tip posted: {topic}")
    
    def _post_quiz(self):
        """Post quiz content"""
        topics = ['Common Mistakes', 'Spellings', 'Synonyms', 'Antonyms', 'Idioms']
        topic = topics[datetime.now().day % len(topics)]
        
        content = self.content_gen.generate_post(topic, 'quiz')
        result = self.fb_poster.post_content(content)
        
        self.db.log_post(
            topic=topic,
            category='quiz',
            content=content,
            post_id=result.get('post_id'),
            status='success' if result['success'] else 'failed'
        )
        
        print(f"🎯 Quiz posted: {topic}")
    
    def _post_idiom(self):
        """Post idiom content"""
        topics = ['Break the ice', 'Piece of cake', 'Hit the sack',
                  'Under the weather', 'Once in a blue moon']
        topic = topics[datetime.now().day % len(topics)]
        
        content = self.content_gen.generate_post(topic, 'idiom')
        result = self.fb_poster.post_content(content)
        
        self.db.log_post(
            topic=topic,
            category='idiom',
            content=content,
            post_id=result.get('post_id'),
            status='success' if result['success'] else 'failed'
        )
        
        print(f"💬 Idiom posted: {topic}")
    
    def start(self):
        """Start the scheduler"""
        self.scheduler.start()
        print("🚀 Post Scheduler Started!")
        print("📅 Schedule:")
        print("  9:00 AM - Word of the Day")
        print("  1:00 PM - Grammar Tip")
        print("  5:00 PM - Quiz Time")
        print("  8:00 PM - Idiom Post")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        print("Scheduler stopped")