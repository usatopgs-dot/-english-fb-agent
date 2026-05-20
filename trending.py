import requests
from datetime import datetime
import random

class TrendingTopics:
    def __init__(self):
        self.cache = {}
        self.cache_time = None
    
    def get_trending_english_topics(self):
        """Get trending English learning topics"""
        # Check cache (refresh every 6 hours)
        if self.cache_time and (datetime.now() - self.cache_time).seconds < 21600:
            return self.cache
        
        trending = {
            'vocabulary': [],
            'grammar': [],
            'idioms': [],
            'quizzes': [],
            'current_trends': []
        }
        
        try:
            # Fetch from multiple free sources
            self._fetch_google_trends(trending)
            self._fetch_seasonal_topics(trending)
            self._fetch_popular_mistakes(trending)
            
        except Exception as e:
            print(f"⚠️ Trending fetch limited: {e}")
            trending = self._get_fallback_trending()
        
        # Add current date based topics
        trending['current_trends'] = self._get_seasonal_topics()
        
        self.cache = trending
        self.cache_time = datetime.now()
        
        return trending
    
    def _fetch_google_trends(self, trending):
        """Fetch trending English language topics"""
        # Simulated trending topics (replace with actual API if available)
        weekly_trends = [
            "AI vocabulary", "Remote work English", "Interview preparation",
            "Email writing", "Presentation skills", "Business idioms",
            "Travel English", "Social media vocabulary", "Tech terms",
            "Environmental vocabulary", "Mental health terms", "Financial English"
        ]
        trending['vocabulary'].extend(random.sample(weekly_trends, 5))
        trending['current_trends'].extend(weekly_trends[:3])
    
    def _fetch_seasonal_topics(self, trending):
        """Add seasonal/holiday related topics"""
        month = datetime.now().month
        day = datetime.now().day
        
        seasonal = {
            1: ["New Year resolutions vocabulary", "Winter idioms", "Goal-setting phrases"],
            2: ["Valentine's Day idioms", "Love expressions", "Friendship vocabulary"],
            3: ["Spring vocabulary", "Women's Day quotes", "Renewal phrases"],
            4: ["Earth Day vocabulary", "Environmental terms", "Spring idioms"],
            5: ["Travel English", "Summer vocabulary", "Memorial Day expressions"],
            6: ["Summer idioms", "Vacation vocabulary", "Father's Day phrases"],
            7: ["Independence vocabulary", "Summer activities terms", "Heat wave expressions"],
            8: ["Back to school vocabulary", "Learning phrases", "Study idioms"],
            9: ["Autumn vocabulary", "Fall idioms", "School terms"],
            10: ["Halloween vocabulary", "Spooky idioms", "Autumn expressions"],
            11: ["Thanksgiving vocabulary", "Gratitude expressions", "Family terms"],
            12: ["Christmas vocabulary", "Holiday idioms", "Winter expressions", "Year-end phrases"]
        }
        
        month_topics = seasonal.get(month, ["English learning tips"])
        trending['vocabulary'].extend(month_topics[:2])
        trending['current_trends'].extend(month_topics[:2])
    
    def _fetch_popular_mistakes(self, trending):
        """Add commonly searched grammar mistakes"""
        common_mistakes = [
            "Your vs You're", "There vs Their vs They're",
            "Affect vs Effect", "Then vs Than", "Who vs Whom",
            "Lay vs Lie", "Fewer vs Less", "Its vs It's",
            "To vs Too vs Two", "Principal vs Principle"
        ]
        trending['grammar'].extend(random.sample(common_mistakes, 4))
    
    def _get_seasonal_topics(self):
        """Get date-specific trending topics"""
        today = datetime.now()
        
        # Special days awareness
        special_days = {
            (1, 1): "New Year English phrases",
            (2, 14): "Valentine's Day love idioms",
            (3, 8): "International Women's Day vocabulary",
            (4, 22): "Earth Day environmental vocabulary",
            (5, 1): "Labor Day expressions",
            (6, 5): "World Environment Day terms",
            (9, 8): "International Literacy Day vocabulary",
            (10, 31): "Halloween spooky vocabulary",
            (12, 25): "Christmas holiday expressions",
            (12, 31): "New Year's Eve phrases"
        }
        
        return [special_days.get((today.month, today.day), "Daily English learning")]
    
    def _get_fallback_trending(self):
        """Fallback trending topics"""
        return {
            'vocabulary': ["Technology terms", "Business English", "Social media vocabulary"],
            'grammar': ["Common mistakes", "Phrasal verbs", "Conditional sentences"],
            'idioms': ["Business idioms", "Sports idioms", "Food idioms"],
            'quizzes': ["Grammar challenge", "Vocabulary test", "Spelling quiz"],
            'current_trends': ["Learn English online", "English for work", "Speaking practice"]
        }
    
    def get_trending_hashtags(self):
        """Get trending English learning hashtags"""
        return [
            "#LearnEnglish", "#ESL", "#EnglishVocabulary",
            "#GrammarTips", "#IdiomOfTheDay", "#WordOfTheDay",
            "#EnglishTeacher", "#StudyEnglish", "#EnglishLanguage",
            "#TOEFL", "#IELTS", "#BusinessEnglish", "#SpeakEnglish"
        ]
