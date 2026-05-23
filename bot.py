import os
import json
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

Commands:

/start
/help
/starttest

Ask SSC questions in Hindi or English.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """
Commands:
/starttest → Start mock test

Ask:
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
                    "content": """You are an expert SSC exam teacher for Indian students.

Rules:
1. Hindi question = Hindi answer
2. English question = English answer
3. Give short exam-focused answers
4. Important facts in bullet points
5. For GK: exact factual answer
6. Mention SSC previous year exam years if known
7. For math: step-by-step shortcut method
8. For reasoning: explain logic clearly
9. Avoid unnecessary long paragraphs
10. Focus only on SSC exam related study help
11. If asked off-topic, politely redirect"""
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
Generate {count} realistic SSC exam level multiple choice questions for {subject} in {language}.

Rules:
1. Real SSC exam difficulty
2. Real exam hall feeling
3. 4 options A B C D
4. Include topic
5. Return ONLY valid JSON

Format:
[
 {{
   "question":"question text",
   "options": {{
      "A":"option",
      "B":"option",
      "C":"option",
      "D":"option"
   }},
   "answer":"A",
   "topic":"Percentage"
 }}
]
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=3000
    )

    return json.loads(response.choices[0].message.content)


async def send_question(query, user_id):
    test = active_tests[user_id]

    if test["current"] >= len(test["questions"]):
        score = test["score"]
        wrong = test["wrong"]
        weak_topics = {}

        for item in test["wrong_topics"]:
            weak_topics[item] = weak_topics.get(item, 0) + 1

        weak_text = "\n".join(
            [f"• {k}: {v} mistakes" for k, v in weak_topics.items()]
        )

        result = f"""
✅ Test Completed

Score: {score}
Wrong Answers: {wrong}

Weak Topics:
{weak_text if weak_text else "None"}

Improvement Tips:
• Practice weak topics daily
• Focus on speed + accuracy
• Revise shortcuts
"""

        await query.edit_message_text(result)
        return

    q = test["questions"][test["current"]]

    keyboard = [
        [
            InlineKeyboardButton("A", callback_data="ans_A"),
            InlineKeyboardButton("B", callback_data="ans_B"),
        ],
        [
            InlineKeyboardButton("C", callback_data="ans_C"),
            InlineKeyboardButton("D", callback_data="ans_D"),
        ],
    ]

    text = f"""
Q{test['current']+1}/{len(test['questions'])}

Topic: {q['topic']}

{q['question']}

A) {q['options']['A']}
B) {q['options']['B']}
C) {q['options']['C']}
D) {q['options']['D']}
"""

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data.startswith("subject_"):
        subject = query.data.replace("subject_", "")

        active_tests[user_id] = {
            "subject": subject,
            "language": None,
            "questions": [],
            "current": 0,
            "score": 0,
            "wrong": 0,
            "wrong_topics": []
        }

        keyboard = [
            [InlineKeyboardButton("English", callback_data="lang_english")],
            [InlineKeyboardButton("Hindi", callback_data="lang_hindi")],
        ]

        await query.edit_message_text(
            "Choose Language:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith("lang_"):
        lang = query.data.replace("lang_", "")
        active_tests[user_id]["language"] = LANGUAGE_MAP[lang]

        keyboard = [
            [InlineKeyboardButton("10 min", callback_data="time_10")],
            [InlineKeyboardButton("15 min", callback_data="time_15")],
            [InlineKeyboardButton("20 min", callback_data="time_20")],
            [InlineKeyboardButton("25 min", callback_data="time_25")],
            [InlineKeyboardButton("30 min", callback_data="time_30")],
        ]

        await query.edit_message_text(
            "Choose Time:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith("time_"):
        mins = int(query.data.replace("time_", ""))
        count = TIME_MAP[mins]

        await query.edit_message_text("Generating exam-level mock test...")

        questions = await generate_questions(
            active_tests[user_id]["subject"],
            count,
            active_tests[user_id]["language"]
        )

        active_tests[user_id]["questions"] = questions
        active_tests[user_id]["current"] = 0

        await send_question(query, user_id)

    elif query.data.startswith("ans_"):
        selected = query.data.replace("ans_", "")
        test = active_tests[user_id]
        q = test["questions"][test["current"]]

        if selected == q["answer"]:
            test["score"] += 2
        else:
            test["score"] -= 0.5
            test["wrong"] += 1
            test["wrong_topics"].append(q["topic"])

        test["current"] += 1
        await send_question(query, user_id)


app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("starttest", start_test))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_ai))

print("Bot running...")
app.run_polling()
