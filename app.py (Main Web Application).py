from flask import Flask, render_template, request, jsonify
from content_generator import ContentGenerator
from facebook_poster import FacebookPoster
from database import Database
from config import Config
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Initialize components
content_gen = ContentGenerator()
fb_poster = FacebookPoster()
db = Database()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'English Learning FB Agent'
    })

@app.route('/api/generate', methods=['POST'])
def generate_post():
    """Generate a post using GLM-5.1"""
    try:
        data = request.json
        topic = data.get('topic', 'English Vocabulary')
        category = data.get('category', 'vocabulary')
        
        content = content_gen.generate_post(topic, category)
        
        return jsonify({
            'success': True,
            'topic': topic,
            'category': category,
            'content': content
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/post', methods=['POST'])
def post_to_facebook():
    """Post content to Facebook"""
    try:
        data = request.json
        content = data.get('content')
        topic = data.get('topic', 'Manual Post')
        category = data.get('category', 'general')
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'Content is required'
            }), 400
        
        result = fb_poster.post_content(content)
        
        # Log to database
        db.log_post(
            topic=topic,
            category=category,
            content=content,
            post_id=result.get('post_id'),
            status='success' if result['success'] else 'failed',
            error=result.get('error')
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats')
def get_stats():
    """Get posting statistics"""
    try:
        stats = db.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recent-posts')
def recent_posts():
    """Get recent posts"""
    try:
        posts = db.get_recent_posts(limit=10)
        posts_data = [{
            'id': post.id,
            'topic': post.topic,
            'category': post.category,
            'status': post.status,
            'created_at': post.created_at.isoformat() if post.created_at else None
        } for post in posts]
        
        return jsonify({
            'success': True,
            'posts': posts_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)