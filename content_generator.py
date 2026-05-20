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
        """Generate English learning post using Qwen 3.5"""
        
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
                    "content": """You are an expert English teacher creating content for a global Facebook page.
                    Follow these rules strictly:
                    1. Write ENTIRELY in English - NO other languages allowed
                    2. Use simple, clear English for learners worldwide
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
            print("❌ API timeout error")
            return self._fallback_post(topic, category)
            
        except Exception as e:
            print(f"❌ API Error: {str(e)}")
            return self._fallback_post(topic, category)
    
    def _create_prompt(self, topic, category):
        """Create category-specific prompts - ENGLISH ONLY"""
        
        prompts = {
            'vocabulary': f"""Create a Facebook post for English learners about the word: "{topic}"
Write ENTIRELY in English. Include:
- Word with emoji
- Simple pronunciation (phonetic spelling like: ri-ZIL-yent)
- Meaning in easy English
- 2 example sentences in daily use
- One easy memory trick in simple English
- Question for followers to engage
- 5-7 hashtags

IMPORTANT: English ONLY. No Hindi, Punjabi, or any other language.""",
            
            'grammar': f"""Create a Facebook grammar lesson post about: "{topic}"
Write ENTIRELY in English. Include:
- Grammar rule explained simply
- 2 correct examples
- 1 common mistake with correction
- Quick tip to remember
- Practice question
- 5-7 hashtags

IMPORTANT: English ONLY. No other languages.""",
            
            'idiom': f"""Create a Facebook post about the English idiom: "{topic}"
Write ENTIRELY in English. Include:
- The idiom
- Its simple meaning
- 2 real-life example sentences
- Fun fact about origin
- Challenge followers to make a sentence
- 5-7 hashtags

IMPORTANT: English ONLY. No other languages.""",
            
            'quiz': f"""Create a fun English quiz post about: "{topic}"
Write ENTIRELY in English. Include:
- Interesting question
- 4 options (A, B, C, D)
- Hint (optional)
- Ask followers to comment their answer
- Mention answer will be revealed later
- 5-7 hashtags

IMPORTANT: English ONLY. No other languages.""",
            
            'general': f"""Create an engaging English learning post about: "{topic}"
Write ENTIRELY in English. Make it:
- Educational but fun
- Easy to understand worldwide
- Shareable content
- Include emojis
- End with a question
- 5-7 hashtags

IMPORTANT: English ONLY. No other languages."""
        }
        
        return prompts.get(category, prompts['general'])
    
    def _fallback_post(self, topic, category):
        """Fallback content if AI fails - English Only"""
        fallbacks = {
            'vocabulary': f"""📚 Word of the Day: {topic}

🌟 Let's expand our English vocabulary together!

📝 Meaning: A new word to enhance your English skills.

💡 Try using "{topic}" in a sentence today!
💬 Comment your sentence below! 👇

❤️ Double tap if you learned something new!

#WordOfTheDay #{topic} #LearnEnglish #Vocabulary #EnglishLearning #ESL #DailyEnglish""",
            
            'grammar': f"""📖 Grammar Lesson: {topic}

✍️ Mastering grammar is key to fluent English!

📌 Save this post for your English practice.

✅ Drop a comment if this was helpful!

#GrammarTips #{topic.replace(' ', '')} #EnglishGrammar #LearnEnglish #EnglishLearning #ESL""",
            
            'idiom': f"""💬 Today's Idiom: {topic}

🗣️ Idioms make your English sound natural!

💡 Challenge: Use this idiom in a sentence below! ⬇️

❤️ Like & Share if you love learning idioms!

#EnglishIdioms #IdiomOfTheDay #{topic.replace(' ', '')} #LearnEnglish #ESL""",
            
            'quiz': f"""🎯 Quick English Quiz!

Topic: {topic}

A) Option 1
B) Option 2
C) Option 3
D) Option 4

Drop your answer in comments! 👇
(Correct answer revealed soon!)

#EnglishQuiz #TestYourEnglish #LearnEnglish #ESL #EnglishLearning""",
            
            'general': f"""📝 English Learning Tip

{topic}

🌟 Every day is an opportunity to improve your English!

💬 What topic should I cover next? Comment below!

#LearnEnglish #EnglishTips #DailyEnglish #EnglishLearning #ESL"""
        }
        return fallbacks.get(category, fallbacks['general'])
    
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
