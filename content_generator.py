import requests
import json
from config import Config
from datetime import datetime

class ContentGenerator:
    def __init__(self):
        self.api_key = Config.GLM_API_KEY
        self.endpoint = Config.GLM_ENDPOINT
        self.model = Config.GLM_MODEL
    
    def generate_post(self, topic, category='vocabulary'):
        """Generate English learning post using GLM-5.1"""
        
        prompt = self._create_prompt(topic, category)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": """You are an expert English teacher creating content for a Facebook page.
                    Follow these rules strictly:
                    1. Write ONLY in English (no other languages)
                    2. Use simple, clear English for learners
                    3. Add relevant emojis (2-4 per post)
                    4. Include line breaks for readability
                    5. End with a question to drive engagement
                    6. Add 5-7 relevant hashtags
                    7. Keep total post under 150 words
                    8. Add an easy memory tip in simple English"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.8,
            "max_tokens": 600,
            "top_p": 0.9
        }
        
        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            print(f"✅ Post generated for: {topic}")
            return content
            
        except requests.exceptions.Timeout:
            print("❌ GLM-5.1 timeout error")
            return self._fallback_post(topic, category)
            
        except Exception as e:
            print(f"❌ GLM-5.1 Error: {str(e)}")
            return self._fallback_post(topic, category)
    
    def _create_prompt(self, topic, category):
        """Create category-specific prompts - ENGLISH ONLY"""
        
        prompts = {
            'vocabulary': f"""Create a Facebook post about the English word: "{topic}"
Write ENTIRELY in English. Include:
- Word with emoji
- Pronunciation (phonetic spelling, like: ri-ZIL-yent)
- Simple meaning in easy English
- 2 example sentences from daily life
- Memory trick in simple English
- Question to engage followers
- 5-7 relevant hashtags

DO NOT use Hindi, Punjabi, or any other language. English ONLY.""",
            
            'grammar': f"""Create a Facebook grammar post about: "{topic}"
Write ENTIRELY in English. Include:
- Grammar rule explained simply
- 2 correct examples
- 1 common mistake with correction
- Quick tip to remember
- Practice question for followers
- 5-7 relevant hashtags

English ONLY.""",
            
            'idiom': f"""Create a Facebook post about the English idiom: "{topic}"
Write ENTIRELY in English. Include:
- The idiom in clear format
- Simple meaning
- 2 example sentences in real situations
- Interesting fact about its origin
- Challenge followers to create their own sentence
- 5-7 relevant hashtags

English ONLY.""",
            
            'quiz': f"""Create a fun English quiz about: "{topic}"
Write ENTIRELY in English. Include:
- Clear question
- 4 options (A, B, C, D)
- Optional hint
- Ask followers to comment their answer
- Mention answer will be revealed later
- 5-7 relevant hashtags

English ONLY.""",
            
            'general': f"""Create an engaging English learning post about: "{topic}"
Write ENTIRELY in English. Make it:
- Educational but fun
- Easy to understand
- Shareable and interesting
- Include relevant emojis
- End with an engaging question
- 5-7 relevant hashtags

English ONLY."""
        }
        
        return prompts.get(category, prompts['general'])
    
    def _fallback_post(self, topic, category):
        """Fallback content if AI fails"""
        return f"""📚 Let's Learn English!

Today's Topic: {topic}

Learn something new every day! 🌟

What would you like to learn next? Comment below! 💬

#LearnEnglish #EnglishLearning #DailyEnglish #{category}"""
    
    def generate_batch(self, topics_list):
        """Generate multiple posts at once"""
        posts = []
        for topic_data in topics_list:
            content = self.generate_post(
                topic_data.get('topic'),
                topic_data.get('category', 'general')
            )
            posts.append({
                'topic': topic_data.get('topic'),
                'category': topic_data.get('category'),
                'content': content,
                'generated_at': datetime.now().isoformat()
            })
        return posts
