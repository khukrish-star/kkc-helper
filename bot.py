import os
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
✅ Maths / Reasoning / English / GK help
✅ Mock Test Mode

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
/start - Start bot
/help - Help
/starttest - Start mock test

Normal SSC questions also supported.
"""
    )


async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Maths", callback_data="subject_maths")],
        [InlineKeyboardButton("Reasoning", callback_data="subject_reasoning")],
        [InlineKeyboardButton("English", callback_data="subject_english")],
        [InlineKeyboardButton("GK", callback_data="subject_gk")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Choose Subject:",
        reply_markup=reply_markup
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

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"Subject Selected: {subject.upper()}\n\nChoose Time:",
            reply_markup=reply_markup
        )

    elif query.data.startswith("time_"):
        minutes = query.data.replace("time_", "")
        question_count = TIME_MAP[minutes]

        if user_id not in active_tests:
            await query.edit_message_text("Session expired. Type /starttest")
            return

        active_tests[user_id]["time"] = minutes
        active_tests[user_id]["questions"] = question_count

        await query.edit_message_text(
            f"""
Mock Test Ready ✅

Subject: {active_tests[user_id]['subject'].upper()}
Time: {minutes} minutes
Questions: {question_count}

Negative Marking:
+2 correct
-0.50 wrong

Part 2 will generate actual questions.
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
3. Short exam-focused answers
4. Maths = step-by-step shortcut
5. Reasoning = logic explanation
6. SSC-focused only"""
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
