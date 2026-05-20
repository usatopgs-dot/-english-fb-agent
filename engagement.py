import random
from datetime import datetime

class EngagementEngine:
    def __init__(self):
        self.quiz_templates = self._load_quiz_templates()
        self.poll_templates = self._load_poll_templates()
    
    def _load_quiz_templates(self):
        """Load quiz/poll templates"""
        return [
            {
                'type': 'grammar',
                'question': "Which sentence is correct?",
                'options': [
                    "A) She don't like coffee",
                    "B) She doesn't like coffee",
                    "C) She not like coffee",
                    "D) She no like coffee"
                ],
                'correct': "B",
                'explanation': "For third person singular (he/she/it), we use 'doesn't' + base verb"
            },
            {
                'type': 'vocabulary',
                'question': "What does 'ubiquitous' mean?",
                'options': [
                    "A) Very rare",
                    "B) Found everywhere",
                    "C) Extremely beautiful",
                    "D) Completely useless"
                ],
                'correct': "B",
                'explanation': "'Ubiquitous' means present, appearing, or found everywhere"
            },
            {
                'type': 'spelling',
                'question': "Which spelling is correct?",
                'options': [
                    "A) Acommodate",
                    "B) Accommodate",
                    "C) Acomodate",
                    "D) Accomodate"
                ],
                'correct': "B",
                'explanation': "Remember: 'Accommodate' has two c's and two m's"
            },
            {
                'type': 'idiom',
                'question': "What does 'break the ice' mean?",
                'options': [
                    "A) To literally break ice",
                    "B) To start a conversation",
                    "C) To end a relationship",
                    "D) To fix a problem"
                ],
                'correct': "B",
                'explanation': "It means to initiate conversation in a social setting"
            },
            {
                'type': 'preposition',
                'question': "I'm interested ___ learning English.",
                'options': [
                    "A) at",
                    "B) on",
                    "C) in",
                    "D) for"
                ],
                'correct': "C",
                'explanation': "We say 'interested in' + noun/gerund"
            }
        ]
    
    def _load_poll_templates(self):
        """Load poll templates"""
        return [
            {
                'question': "What's the hardest part of learning English?",
                'options': ["Grammar", "Vocabulary", "Pronunciation", "Speaking fluently"],
                'duration': "24 hours"
            },
            {
                'question': "How do you prefer to learn English?",
                'options': ["Reading books", "Watching videos", "Apps/Duolingo", "Conversation practice"],
                'duration': "24 hours"
            },
            {
                'question': "Which English skill do you want to improve most?",
                'options': ["Speaking", "Writing", "Listening", "Reading"],
                'duration': "24 hours"
            },
            {
                'question': "How long have you been learning English?",
                'options': ["< 6 months", "6-12 months", "1-3 years", "> 3 years"],
                'duration': "24 hours"
            }
        ]
    
    def generate_quiz_post(self):
        """Generate a quiz/poll post"""
        quiz = random.choice(self.quiz_templates)
        
        post = f"""🎯 Quick English Challenge! 🧠

{quiz['question']}

{chr(10).join(quiz['options'])}

🤔 Think carefully! What's your answer?

💬 Comment your answer (A, B, C, or D) below!
⏰ I'll reveal the correct answer in 2 hours!

❤️ Like if you find this helpful!
🔖 Save for later practice!

#EnglishQuiz #{quiz['type'].title()} #LearnEnglish #ESL #TestYourEnglish #EnglishChallenge"""
        
        return post, quiz['correct'], quiz['explanation']
    
    def generate_poll_post(self):
        """Generate a Facebook poll"""
        poll = random.choice(self.poll_templates)
        
        post = f"""📊 Quick Poll: Help Me Help You! 🤝

{poll['question']}

Your options:
{chr(10).join([f'{i+1}. {opt}' for i, opt in enumerate(poll['options'])])}

👇 Vote by commenting the NUMBER below!
⏰ Poll closes in {poll['duration']}!

Your feedback helps me create better content for YOU! 💙

#Poll #EnglishLearning #LearnEnglish #ESL #CommunityVote"""
        
        return post, poll['options']
    
    def generate_fill_in_blank(self):
        """Generate fill-in-the-blank exercise"""
        exercises = [
            {"sentence": "She ___ (go) to the market every Sunday.", "answer": "goes", "hint": "Present Simple, 3rd person"},
            {"sentence": "I ___ (never/be) to Paris.", "answer": "have never been", "hint": "Present Perfect"},
            {"sentence": "If I ___ (be) rich, I would travel the world.", "answer": "were", "hint": "Subjunctive mood"},
            {"sentence": "The book ___ (write) by Shakespeare.", "answer": "was written", "hint": "Passive Voice"},
            {"sentence": "She asked me if I ___ (can) help her.", "answer": "could", "hint": "Reported Speech"}
        ]
        
        exercise = random.choice(exercises)
        
        post = f"""✍️ Fill in the Blank Challenge!

📝 Complete this sentence:
"{exercise['sentence']}"

💡 Hint: {exercise['hint']}

💬 Write your answer in the comments!
✅ I'll reply with the correct answer!

Challenge your friends - share this post! 🔄

#FillInTheBlank #EnglishPractice #Grammar #LearnEnglish #ESL"""
        
        return post, exercise['answer']
    
    def generate_engagement_reply(self, correct_answer, explanation):
        """Generate reply for commenters"""
        return f"""✅ Correct answer: {correct_answer}

📚 Explanation: {explanation}

Well done to everyone who got it right! 🎉
Those who didn't - don't worry, that's how we learn! 💪

More quizzes coming soon! Stay tuned! 🚀"""

# Database update function (add to database.py)
def update_database_for_engagement():
    """SQL to add engagement tracking columns"""
    sql_statements = """
    ALTER TABLE post_logs ADD COLUMN likes INTEGER DEFAULT 0;
    ALTER TABLE post_logs ADD COLUMN comments INTEGER DEFAULT 0;
    ALTER TABLE post_logs ADD COLUMN shares INTEGER DEFAULT 0;
    ALTER TABLE post_logs ADD COLUMN engagement_score INTEGER DEFAULT 0;
    """
    return sql_statements
