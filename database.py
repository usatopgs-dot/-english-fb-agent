from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class PostLog(Base):
    __tablename__ = 'post_logs'
    
    id = Column(Integer, primary_key=True)
    topic = Column(String(200))
    category = Column(String(50))
    content = Column(Text)
    post_id = Column(String(100))
    status = Column(String(20))  # success, failed, pending
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    posted_at = Column(DateTime)

class Database:
    def __init__(self):
        db_path = os.path.join(os.path.dirname(__file__), 'posts.db')
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def log_post(self, topic, category, content, post_id=None, status='success', error=None):
        """Log post details to database"""
        log = PostLog(
            topic=topic,
            category=category,
            content=content,
            post_id=post_id,
            status=status,
            error_message=error,
            posted_at=datetime.now() if status == 'success' else None
        )
        self.session.add(log)
        self.session.commit()
        return log.id
    
    def get_recent_posts(self, limit=10):
        """Get recent posts"""
        return self.session.query(PostLog).order_by(
            PostLog.created_at.desc()
        ).limit(limit).all()
    
    def get_stats(self):
        """Get posting statistics"""
        total = self.session.query(PostLog).count()
        successful = self.session.query(PostLog).filter_by(status='success').count()
        failed = self.session.query(PostLog).filter_by(status='failed').count()
        
        return {
            'total_posts': total,
            'successful_posts': successful,
            'failed_posts': failed
        }
