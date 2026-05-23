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

WELCOME_TEXT = """
🎓 SSC Study Assistant Bot

Features:
✅ SSC Q&A
✅ Mock Tests
✅ Subject Practice

Commands:
/start
/help
/starttest
"""

TIME_MAP = {
    "10": 8,
    "15": 12,
    "20": 15,
    "25": 20,
    "30": 25,
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """
Commands:
/start
/help
/starttest
"""
    )


async def generate_questions(subject, count):
    prompt = f"""
Generate {count} realistic SSC exam level multiple choice questions for {subject}.

Rules:
1. Real SSC exam difficulty
2. Questions should feel like exam hall level
3. 4 options A, B, C, D
4. Include topic name
5. Return ONLY valid JSON list

Format:
[
 {{
   "question": "question text",
   "options": {{
      "A": "option A",
      "B": "option B",
      "C": "option C",
      "D": "option D"
   }},
   "answer": "A",
   "topic": "Percentage"
 }}
]
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=3000
    )

    content = response.choices[0].message.content
    return json.loads(content)


async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Maths", callback_data="subject_maths")],
        [InlineKeyboardButton("Reasoning", callback_data="subject_reasoning")],
        [InlineKeyboardButton("English", callback_data="subject_english")],
        [InlineKeyboardButton("GK", callback_data="subject_gk")],
    ]

    await update.message.reply_text(
        "Choose Subject:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def send_question(query, user_id):
    test = active_tests[user_id]
    current = test["current"]

    if current >= len(test["questions"]):
        await query.message.reply_text("Test completed. Part 3 will add scoring.")
        return

    q = test["questions"][current]

    keyboard = [
        [
            InlineKeyboardButton("A", callback_data="answer_A"),
            InlineKeyboardButton("B", callback_data="answer_B"),
        ],
        [
            InlineKeyboardButton("C", callback_data="answer_C"),
            InlineKeyboardButton("D", callback_data="answer_D"),
        ]
    ]

    text = f"""
Q{current+1}/{len(test['questions'])}

Topic: {q['topic']}

{q['question']}

A) {q['options']['A']}
B) {q['options']['B']}
C) {q['options']['C']}
D) {q['options']['D']}
"""

    await query.message.reply_text(
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
            "subject": subject
        }

        keyboard = [
            [InlineKeyboardButton("10 min", callback_data="time_10")],
            [InlineKeyboardButton("15 min", callback_data="time_15")],
            [InlineKeyboardButton("20 min", callback_data="time_20")],
            [InlineKeyboardButton("25 min", callback_data="time_25")],
            [InlineKeyboardButton("30 min", callback_data="time_30")],
        ]

        await query.edit_message_text(
            f"Subject Selected: {subject.upper()}\n\nChoose Time:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith("time_"):
        minutes = query.data.replace("time_", "")
        question_count = TIME_MAP[minutes]

        await query.edit_message_text("Generating realistic SSC questions...")

        questions = await generate_questions(
            active_tests[user_id]["subject"],
            question_count
        )

        active_tests[user_id]["time"] = minutes
        active_tests[user_id]["questions"] = questions
        active_tests[user_id]["current"] = 0
        active_tests[user_id]["answers"] = []

        await send_question(query, user_id)

    elif query.data.startswith("answer_"):
        answer = query.data.replace("answer_", "")

        active_tests[user_id]["answers"].append(answer)
        active_tests[user_id]["current"] += 1

        await send_question(query, user_id)


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
1. Hindi = Hindi
2. English = English
3. SSC-focused answers
4. Short clear explanations"""
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


app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("starttest", start_test))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_ai))

print("Bot running...")
app.run_polling()
