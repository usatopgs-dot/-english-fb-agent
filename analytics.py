from database import Database
from datetime import datetime, timedelta
import json

class SmartScheduler:
    def __init__(self):
        self.db = Database()
        
    def get_best_posting_times(self, days=30):
        """Analyze last 30 days posts to find best times"""
        posts = self.db.get_all_posts(days=days)
        
        if not posts:
            # Default best times if no data
            return self._get_default_times()
        
        # Group posts by hour and calculate engagement
        hourly_stats = {}
        for post in posts:
            if post.get('posted_at'):
                hour = post['posted_at'].hour
                if hour not in hourly_stats:
                    hourly_stats[hour] = {'count': 0, 'likes': 0, 'score': 0}
                hourly_stats[hour]['count'] += 1
                hourly_stats[hour]['likes'] += post.get('likes', 0)
                hourly_stats[hour]['score'] += post.get('engagement_score', 0)
        
        # Calculate average engagement per hour
        best_times = []
        for hour, stats in hourly_stats.items():
            if stats['count'] > 0:
                avg_score = stats['score'] / stats['count']
                best_times.append({
                    'hour': hour,
                    'score': avg_score,
                    'posts': stats['count']
                })
        
        # Sort by engagement score
        best_times.sort(key=lambda x: x['score'], reverse=True)
        
        return best_times[:4] if best_times else self._get_default_times()
    
    def _get_default_times(self):
        """Default posting times based on research"""
        return [
            {'hour': 7, 'score': 0, 'label': 'Morning Peak'},
            {'hour': 12, 'score': 0, 'label': 'Lunch Break'},
            {'hour': 17, 'score': 0, 'label': 'Evening Commute'},
            {'hour': 20, 'score': 0, 'label': 'Night Learning'}
        ]
    
    def update_schedule(self):
        """Update posting schedule based on analytics"""
        best_times = self.get_best_posting_times()
        
        # Round to nearest hour for simplicity
        schedule = []
        for time_data in best_times[:4]:
            hour = time_data['hour']
            schedule.append({
                'hour': hour,
                'minute': 0,
                'label': time_data.get('label', f'{hour}:00'),
                'score': time_data['score']
            })
        
        # Sort by hour
        schedule.sort(key=lambda x: x['hour'])
        
        return schedule
    
    def get_time_insights(self):
        """Get human-readable insights"""
        best_times = self.get_best_posting_times()
        insights = []
        
        for i, time_data in enumerate(best_times[:4]):
            hour = time_data['hour']
            period = "AM" if hour < 12 else "PM"
            display_hour = hour if hour <= 12 else hour - 12
            if display_hour == 0:
                display_hour = 12
            
            insights.append({
                'rank': i + 1,
                'time': f"{display_hour}:00 {period}",
                'hour': hour,
                'effectiveness': '⭐' * (5 - i) if i < 5 else '⭐',
                'label': time_data.get('label', '')
            })
        
        return insights
