import os
import json
import time
from groq import Groq
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

active_tests = {}

TIME_MAP = {
    10: 8,
    15: 12,
    20: 16,
    25: 20,
    30: 25
}

LANGUAGE_MAP = {
    "english": "English",
    "hindi": "Hindi"
}

WELCOME_TEXT = """
🎓 SSC Study Assistant Bot

Features:
✅ SSC Q&A
✅ Mock Tests
✅ Weak Topic Analysis
✅ Performance Report

Commands:
/start
/help
/starttest
"""

def safe_json_parse(content):
    try:
        return json.loads(content)
    except:
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)

def get_performance(score, total):
    percent = (score / total) * 100

    if percent >= 85:
        return "🔥 Excellent Exam Readiness", "Very strong performance. Maintain consistency."
    elif percent >= 70:
        return "⚡ Strong Performer", "Good preparation. Improve speed + accuracy."
    elif percent >= 50:
        return "📘 Average Performer", "Need regular mock practice."
    else:
        return "⚠️ Needs Serious Improvement", "Focus on basics and daily practice."

def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins} min {secs} sec"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """
Commands:
/starttest → Start Mock Test

Ask any SSC question:
भारत का संविधान कब लागू हुआ?
Percentage shortcut trick
Reasoning puzzle
"""
    )


async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    wait_msg = await update.message.reply_text("Thinking...")

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert SSC exam teacher.

Rules:
1. Hindi question = Hindi answer
2. English question = English answer
3. Give short exam-focused answers
4. Mention SSC previous year exam if likely known
5. For math: step-by-step shortcut
6. For reasoning: explain logic
7. Focus only on SSC preparation"""
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=0.3,
            max_tokens=1000
        )

        answer = response.choices[0].message.content
        await wait_msg.edit_text(answer[:4000])

    except Exception as e:
        await wait_msg.edit_text(f"AI Error:\n{str(e)}")


async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("GK", callback_data="subject_gk")],
        [InlineKeyboardButton("Math", callback_data="subject_math")],
        [InlineKeyboardButton("Reasoning", callback_data="subject_reasoning")],
        [InlineKeyboardButton("English", callback_data="subject_english")],
    ]

    await update.message.reply_text(
        "Choose Subject:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def generate_questions(subject, count, language):
    prompt = f"""
Generate {count} realistic SSC exam level MCQs for {subject} in {language}.

Rules:
1. Real SSC exam difficulty
2. Exam hall level quality
3. 4 options A B C D
4. Include topic
5. Include likely exam and year
6. Return ONLY JSON

Format:
[
 {{
   "question":"question",
   "options": {{
      "A":"option",
      "B":"option",
      "C":"option",
      "D":"option"
   }},
   "answer":"A",
   "topic":"Percentage",
   "exam":"SSC CGL",
   "year":"2022"
 }}
]
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=4000
    )

    content = response.choices[0].message.content
    return safe_json_parse(content)
