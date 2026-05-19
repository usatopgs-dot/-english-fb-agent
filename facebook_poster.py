import facebook
from datetime import datetime
from config import Config

class FacebookPoster:
    def __init__(self):
        self.page_id = Config.FB_PAGE_ID
        self.access_token = Config.FB_ACCESS_TOKEN
        self.graph = facebook.GraphAPI(access_token=self.access_token)
    
    def post_content(self, message, media_url=None):
        """Post to Facebook page"""
        try:
            if media_url:
                # Post with image
                with open(media_url, 'rb') as image:
                    post_id = self.graph.put_photo(
                        image=image,
                        message=message
                    )
            else:
                # Text post
                post_id = self.graph.put_object(
                    parent_object=self.page_id,
                    connection_name='feed',
                    message=message
                )
            
            print(f"✅ Posted to Facebook: {post_id['id']}")
            return {
                'success': True,
                'post_id': post_id['id'],
                'timestamp': datetime.now().isoformat()
            }
            
        except facebook.GraphAPIError as e:
            print(f"❌ Facebook Error: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def schedule_post(self, content, schedule_time):
        """Schedule a post for later"""
        # Facebook doesn't support native scheduling via API easily
        # We'll handle scheduling in our app logic
        return {
            'content': content[:100] + '...',
            'scheduled_for': schedule_time.isoformat()
        }
