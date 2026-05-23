import os
import random
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

QUESTION_BANK = {
    "gk": [
        {
            "question": "भारत का संविधान कब लागू हुआ?",
            "options": {
                "A": "26 January 1950",
                "B": "15 August 1947",
                "C": "26 November 1949",
                "D": "2 October 1949"
            },
            "answer": "A"
        }
    ],
    "math": [
        {
            "question": "25 × 4 = ?",
            "options": {
                "A": "50",
                "B": "75",
                "C": "100",
                "D": "125"
            },
            "answer": "C"
        }
    ],
    "reasoning": [
        {
            "question": "A, C, E, ?",
            "options": {
                "A": "F",
                "B": "G",
                "C": "H",
                "D": "I"
            },
            "answer": "B"
        }
    ],
    "english": [
        {
            "question": "Choose synonym of Happy",
            "options": {
                "A": "Sad",
                "B": "Joyful",
                "C": "Angry",
                "D": "Weak"
            },
            "answer": "B"
        }
    ]
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("KKC Helper Bot Active ✅")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start\n/help\n/starttest\n\nAsk SSC questions directly."
    )


async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=0.3,
            max_tokens=800
        )

        answer = response.choices[0].message.content
        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text(f"AI Error: {str(e)}")


async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("GK", callback_data="gk")],
        [InlineKeyboardButton("Math", callback_data="math")],
        [InlineKeyboardButton("Reasoning", callback_data="reasoning")],
        [InlineKeyboardButton("English", callback_data="english")]
    ]

    await update.message.reply_text(
        "Choose Subject:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    subject = query.data

    if subject in QUESTION_BANK:
        question = random.choice(QUESTION_BANK[subject])

        active_tests[user_id] = question

        keyboard = [
            [
                InlineKeyboardButton("A", callback_data="ans_A"),
                InlineKeyboardButton("B", callback_data="ans_B")
            ],
            [
                InlineKeyboardButton("C", callback_data="ans_C"),
                InlineKeyboardButton("D", callback_data="ans_D")
            ]
        ]

        text = (
            f"{question['question']}\n\n"
            f"A) {question['options']['A']}\n"
            f"B) {question['options']['B']}\n"
            f"C) {question['options']['C']}\n"
            f"D) {question['options']['D']}"
        )

        await query.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith("ans_"):
        if user_id not in active_tests:
            await query.message.reply_text("No active test.")
            return

        selected = query.data.replace("ans_", "")
        correct = active_tests[user_id]["answer"]

        if selected == correct:
            await query.message.reply_text("✅ Correct")
        else:
            await query.message.reply_text(
                f"❌ Wrong. Correct Answer: {correct}"
            )

        del active_tests[user_id]


app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("starttest", start_test))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_ai))

print("Bot running...")
app.run_polling()
