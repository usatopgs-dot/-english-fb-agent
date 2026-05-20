import sqlite3
import os
from datetime import datetime, timedelta

class Database:
    def __init__(self):
        db_path = os.path.join(os.path.dirname(__file__), 'posts.db')
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        """Create all tables if not exists"""
        # Main posts table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                category TEXT,
                content TEXT,
                post_id TEXT,
                status TEXT,
                error_message TEXT,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                engagement_score INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                posted_at TIMESTAMP
            )
        ''')
        
        # Course tracking table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS course_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_name TEXT,
                day_number INTEGER,
                topic TEXT,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Analytics cache table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                best_hour INTEGER,
                engagement_score REAL,
                post_count INTEGER,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Try to add new columns (ignore if already exist)
        try:
            self.cursor.execute('ALTER TABLE post_logs ADD COLUMN likes INTEGER DEFAULT 0')
        except:
            pass
        try:
            self.cursor.execute('ALTER TABLE post_logs ADD COLUMN comments INTEGER DEFAULT 0')
        except:
            pass
        try:
            self.cursor.execute('ALTER TABLE post_logs ADD COLUMN shares INTEGER DEFAULT 0')
        except:
            pass
        try:
            self.cursor.execute('ALTER TABLE post_logs ADD COLUMN engagement_score INTEGER DEFAULT 0')
        except:
            pass
        
        self.conn.commit()
    
    # ========== POST LOGGING ==========
    
    def log_post(self, topic, category, content, post_id=None, status='success', error=None):
        """Log post details to database"""
        posted_at = datetime.now().isoformat() if status == 'success' else None
        self.cursor.execute('''
            INSERT INTO post_logs (topic, category, content, post_id, status, error_message, posted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (topic, category, content, post_id, status, error, posted_at))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_post_status(self, internal_id, status, post_id=None, error=None):
        """Update post status after posting"""
        posted_at = datetime.now().isoformat() if status == 'success' else None
        self.cursor.execute('''
            UPDATE post_logs 
            SET status=?, post_id=?, error_message=?, posted_at=?
            WHERE id=?
        ''', (status, post_id, error, posted_at, internal_id))
        self.conn.commit()
    
    def update_engagement(self, post_id, likes=0, comments=0, shares=0):
        """Update post engagement stats from Facebook insights"""
        engagement_score = likes + (comments * 2) + (shares * 3)
        self.cursor.execute('''
            UPDATE post_logs 
            SET likes=?, comments=?, shares=?, engagement_score=?
            WHERE post_id=?
        ''', (likes, comments, shares, engagement_score, post_id))
        self.conn.commit()
    
    # ========== ANALYTICS METHODS ==========
    
    def get_all_posts(self, days=30):
        """Get all posts from last N days for analytics"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        self.cursor.execute('''
            SELECT id, topic, category, content, post_id, status, 
                   likes, comments, shares, engagement_score, 
                   created_at, posted_at
            FROM post_logs 
            WHERE posted_at >= ?
            ORDER BY posted_at DESC
        ''', (cutoff,))
        
        columns = ['id', 'topic', 'category', 'content', 'post_id', 'status',
                   'likes', 'comments', 'shares', 'engagement_score', 
                   'created_at', 'posted_at']
        posts = []
        for row in self.cursor.fetchall():
            post = dict(zip(columns, row))
            # Convert posted_at string to datetime object for analytics
            if post.get('posted_at'):
                try:
                    post['posted_at'] = datetime.fromisoformat(post['posted_at'])
                except:
                    pass
            posts.append(post)
        return posts
    
    def get_posts_by_category(self, category, days=30):
        """Get posts filtered by category"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        self.cursor.execute('''
            SELECT * FROM post_logs 
            WHERE category=? AND posted_at >= ?
            ORDER BY posted_at DESC
        ''', (category, cutoff))
        return self.cursor.fetchall()
    
    def get_best_performing_posts(self, limit=5):
        """Get posts with highest engagement"""
        self.cursor.execute('''
            SELECT topic, category, engagement_score, likes, comments, shares, posted_at
            FROM post_logs 
            WHERE status='success' AND engagement_score > 0
            ORDER BY engagement_score DESC
            LIMIT ?
        ''', (limit,))
        columns = ['topic', 'category', 'engagement_score', 'likes', 'comments', 'shares', 'posted_at']
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    # ========== RECENT POSTS ==========
    
    def get_recent_posts(self, limit=10):
        """Get recent posts for dashboard"""
        self.cursor.execute('''
            SELECT id, topic, category, status, post_id, 
                   likes, comments, engagement_score, created_at 
            FROM post_logs 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        columns = ['id', 'topic', 'category', 'status', 'post_id',
                   'likes', 'comments', 'engagement_score', 'created_at']
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    # ========== STATISTICS ==========
    
    def get_stats(self):
        """Get overall posting statistics"""
        self.cursor.execute('SELECT COUNT(*) FROM post_logs')
        total = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM post_logs WHERE status='success'")
        successful = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM post_logs WHERE status='failed'")
        failed = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM post_logs WHERE posted_at >= ?", 
                           ((datetime.now() - timedelta(hours=24)).isoformat(),))
        today_total = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT SUM(likes), SUM(comments), SUM(shares) FROM post_logs")
        total_engagement = self.cursor.fetchone()
        
        return {
            'total_posts': total,
            'successful_posts': successful,
            'failed_posts': failed,
            'today_posts': today_total,
            'total_likes': total_engagement[0] or 0,
            'total_comments': total_engagement[1] or 0,
            'total_shares': total_engagement[2] or 0,
            'total_engagement': (total_engagement[0] or 0) + (total_engagement[1] or 0) * 2 + (total_engagement[2] or 0) * 3
        }
    
    def get_daily_stats(self, days=7):
        """Get day-by-day stats for charts"""
        stats = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            self.cursor.execute('''
                SELECT COUNT(*), SUM(likes), SUM(comments), SUM(shares)
                FROM post_logs 
                WHERE DATE(posted_at) = ?
            ''', (date,))
            row = self.cursor.fetchone()
            stats.append({
                'date': date,
                'posts': row[0] or 0,
                'likes': row[1] or 0,
                'comments': row[2] or 0,
                'shares': row[3] or 0
            })
        return stats
    
    # ========== COURSE TRACKING ==========
    
    def log_course_day(self, course_name, day_number, topic):
        """Log course progress"""
        self.cursor.execute('''
            INSERT INTO course_progress (course_name, day_number, topic)
            VALUES (?, ?, ?)
        ''', (course_name, day_number, topic))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_course_progress(self, course_name):
        """Get completed days for a course"""
        self.cursor.execute('''
            SELECT COUNT(*) FROM course_progress 
            WHERE course_name=?
        ''', (course_name,))
        return self.cursor.fetchone()[0]
    
    def get_course_days(self, course_name):
        """Get all completed course days"""
        self.cursor.execute('''
            SELECT day_number, topic, completed_at 
            FROM course_progress 
            WHERE course_name=?
            ORDER BY day_number
        ''', (course_name,))
        return self.cursor.fetchall()
    
    # ========== ANALYTICS CACHE ==========
    
    def cache_analytics(self, best_hour, engagement_score, post_count):
        """Cache analytics results"""
        self.cursor.execute('''
            INSERT INTO analytics_cache (best_hour, engagement_score, post_count)
            VALUES (?, ?, ?)
        ''', (best_hour, engagement_score, post_count))
        self.conn.commit()
    
    def get_cached_analytics(self, hours=24):
        """Get recent cached analytics"""
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        self.cursor.execute('''
            SELECT * FROM analytics_cache 
            WHERE calculated_at >= ?
            ORDER BY calculated_at DESC
        ''', (cutoff,))
        return self.cursor.fetchall()
    
    # ========== MAINTENANCE ==========
    
    def cleanup_old_logs(self, days=90):
        """Remove logs older than N days (optional)"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        self.cursor.execute('DELETE FROM post_logs WHERE created_at < ?', (cutoff,))
        self.cursor.execute('DELETE FROM analytics_cache WHERE calculated_at < ?', (cutoff,))
        self.conn.commit()
        return self.cursor.rowcount
    
    def get_table_info(self):
        """Get database table information"""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = self.cursor.fetchall()
        info = {}
        for table in tables:
            table_name = table[0]
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = self.cursor.fetchone()[0]
            info[table_name] = count
        return info
    
    def close(self):
        """Close database connection"""
        self.conn.close()
