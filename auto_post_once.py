"""Runs once - generates ONE post and publishes to Facebook"""
import requests
import os
from datetime import datetime
import random

# API Keys from environment
API_KEY = os.getenv('GLM_API_KEY')
ENDPOINT = os.getenv('GLM_ENDPOINT', 'https://integrate.api.nvidia.com/v1/chat/completions')
MODEL = os.getenv('GLM_MODEL', 'qwen/qwen3.5-397b-a17b')
FB_PAGE_ID = os.getenv('FB_PAGE_ID')
FB_TOKEN = os.getenv('FB_ACCESS_TOKEN')

def get_category():
    """Determine category based on time"""
    hour = datetime.utcnow().hour
    
    # Convert UTC to IST (UTC+5:30)
    ist_hour = (hour + 5) % 24
    ist_hour += 0.5 if datetime.utcnow().minute >= 30 else 0
    
    if 5 <= ist_hour < 9:
        return 'vocabulary', "Create a Word of the Day post. Choose an interesting English word YOURSELF. Include: pronunciation, meaning, 2 examples, memory tip, engagement question, and 5-7 hashtags."
    elif 9 <= ist_hour < 13:
        return 'grammar', "Create a grammar tip post. Choose a grammar topic YOURSELF that learners find confusing. Include: simple explanation, 2 correct examples, 1 common mistake with correction, practice question, and 5-7 hashtags."
    elif 13 <= ist_hour < 17:
        return 'quiz', "Create an English quiz post. Choose a quiz topic YOURSELF. Include: interesting question, 4 options (A-D), hint, ask for comments, and 5-7 hashtags."
    elif 17 <= ist_hour < 21:
        return 'idiom', "Create an idiom post. Choose a useful English idiom YOURSELF. Include: idiom, simple meaning, 2 real-life examples, fun fact, challenge for followers, and 5-7 hashtags."
    else:
        return 'vocabulary', "Create a Word of the Day post. Choose an interesting word YOURSELF. Include: pronunciation, meaning, examples, and hashtags."

def get_fallback(category):
    """Fallback posts if AI fails"""
    fallbacks = {
        'vocabulary': """📚 Word of the Day: Resilience 🌱

Pronunciation: ri-ZIL-yent

Meaning: The ability to recover quickly from difficulties or setbacks.

Examples:
→ "Despite losing her job, she showed great resilience and found a new career within a month."
→ "Children are naturally resilient; they adapt to changes faster than adults."

Memory Tip: Think of a rubber band - no matter how far you stretch it, it bounces right back!

Your Turn: When did you show resilience in a difficult situation? Share your story below! 👇

#WordOfTheDay #EnglishVocabulary #LearnEnglish #Resilience #ESL #EnglishLearning #DailyEnglish""",

        'grammar': """📖 Grammar Focus: Present Perfect vs Past Simple

Many learners mix these up! Here is the easy way:

PRESENT PERFECT: have/has + past participle
→ Use for past actions with present connection
→ Example: "I have visited Paris three times." (The experience matters now)

PAST SIMPLE: verb + ed/irregular
→ Use for completed past actions with specific time
→ Example: "I visited Paris last summer." (Specific time given)

Common Mistake:
❌ "I have visited Paris yesterday." 
✅ "I visited Paris yesterday."
(Do not use present perfect with specific past time!)

Practice: Fill in the blank:
"She ___ (live) in London since 2019."

Drop your answer! 👇

#GrammarTips #PresentPerfect #EnglishGrammar #LearnEnglish #ESL #EnglishTeacher""",

        'quiz': """🎯 Quick English Challenge! 🧠

Which sentence is grammatically correct?

A) If I was rich, I would travel the world.
B) If I were rich, I would travel the world.
C) If I am rich, I would travel the world.
D) If I will be rich, I would travel the world.

Think carefully about conditionals! 🤔

Comment your answer (A, B, C, or D) below! 👇
Correct answer revealed in 2 hours!

#EnglishQuiz #GrammarChallenge #Conditionals #LearnEnglish #ESL #TestYourEnglish""",

        'idiom': """💬 Idiom of the Day: Break the Ice 🧊

Meaning: To start a conversation in a social setting and make people feel more comfortable.

Examples in action:
→ "The teacher used a fun game to break the ice on the first day of class."
→ "At the networking event, John told a joke to break the ice with the other professionals."

Fun Fact: Ships would sometimes get stuck in ice. Smaller boats called 'icebreakers' would go ahead to 'break the ice' and clear a path! 🚢

Your Turn: How do YOU break the ice when meeting new people? Share your tips! 👇

#IdiomOfTheDay #BreakTheIce #EnglishIdioms #LearnEnglish #ESL #SpeakEnglish"""
    }
    return fallbacks.get(category, fallbacks['vocabulary'])

def generate_post(category, instruction):
    """Generate post using Qwen 3.5 AI"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": """You are an expert English teacher creating viral Facebook posts.

CRITICAL FORMATTING RULES:
1. Write in PLAIN TEXT only - absolutely NO Markdown formatting!
2. NEVER use ** asterisks ** for bold or emphasis
3. NEVER use * single asterisks * for italic
4. NEVER use __ underscores __ for underline
5. NEVER use backticks ` for code
6. Use EMOJIS 📚 and LINE BREAKS for visual formatting instead
7. Use CAPITAL LETTERS for emphasis when needed
8. Use arrows → or dashes - for lists, not markdown bullets
9. Use emoji bullets like ✅ ❌ 📝 💡 instead of markdown

EXAMPLE OF WRONG FORMAT (DO NOT DO THIS):
"**Word of the Day** is **Resilient**" 

EXAMPLE OF RIGHT FORMAT (DO THIS):
"🌟 Word of the Day: Resilient"

Choose topics YOURSELF. Be creative, original, and never repeat. 
Write ENTIRELY in English. 
Add 5-7 relevant hashtags at the end.
Keep under 200 words.
End with an engagement question."""
            },
            {"role": "user", "content": instruction}
        ],
        "temperature": 0.95,
        "max_tokens": 500,
        "top_p": 0.9
    }
    
    try:
        response = requests.post(ENDPOINT, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Clean any remaining markdown
            content = content.replace('**', '')
            content = content.replace('__', '')
            
            # Check quality
            if len(content) > 50 and '#' in content:
                return content
            else:
                print(f"⚠️ Content quality check failed, using fallback")
    except Exception as e:
        print(f"❌ AI Error: {e}")
    
    # Return fallback if AI fails
    return get_fallback(category)

def post_to_facebook(content):
    """Post content to Facebook page"""
    try:
        import facebook
        graph = facebook.GraphAPI(access_token=FB_TOKEN)
        result = graph.put_object(
            parent_object=FB_PAGE_ID,
            connection_name='feed',
            message=content
        )
        print(f"✅ Posted! ID: {result['id']}")
        return result['id']
    except Exception as e:
        print(f"❌ Facebook Error: {e}")
        return None

def main():
    """Main function - runs once per GitHub Action trigger"""
    print(f"🕐 Starting at: {datetime.utcnow()} UTC")
    print(f"📅 IST Time: {(datetime.utcnow().hour + 5) % 24}:{datetime.utcnow().minute:02d}")
    
    category, instruction = get_category()
    print(f"📂 Category: {category}")
    print(f"📝 Instruction: {instruction[:80]}...")
    
    print("🧠 Generating post with Qwen 3.5 AI...")
    content = generate_post(category, instruction)
    
    print(f"✅ Generated ({len(content)} chars)")
    print(f"📝 Preview: {content[:120]}...")
    
    # Check for markdown
    if '**' in content:
        print("⚠️ WARNING: Post contains markdown, cleaning...")
        content = content.replace('**', '')
    
    print("📤 Posting to Facebook...")
    post_id = post_to_facebook(content)
    
    if post_id:
        print(f"🎉 SUCCESS! Post ID: {post_id}")
        print(f"🔗 View at: https://facebook.com/{FB_PAGE_ID}")
    else:
        print("❌ FAILED to post to Facebook")

if __name__ == '__main__':
    main()
