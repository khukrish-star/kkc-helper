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
        },
        {
            "question": "भारत की राजधानी क्या है?",
            "options": {
                "A": "Mumbai",
                "B": "Delhi",
                "C": "Kolkata",
                "D": "Chennai"
            },
            "answer": "B"
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
        },
        {
            "question": "144 ÷ 12 = ?",
            "options": {
                "A": "10",
                "B": "11",
                "C": "12",
                "D": "13"
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
        },
        {
            "question": "2, 4, 8, 16, ?",
            "options": {
                "A": "24",
                "B": "30",
                "C": "32",
                "D": "36"
            },
            "answer": "C"
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
        },
        {
            "question": "Choose antonym of Fast",
            "options": {
                "A": "Quick",
                "B": "Rapid",
                "C": "Slow",
                "D": "Swift"
            },
            "answer": "C"
        }
    ]
}


def get_question(subject):
    return random.choice(QUESTION_BANK[subject])


async def send_question(chat, question):
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

    await chat.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "KKC Helper Bot Active ✅\n\n"
        "/start\n"
        "/help\n"
        "/starttest\n\n"
        "Ask SSC questions directly."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start → Start bot\n"
        "/help → Help\n"
        "/starttest → Mock test\n"
    )


async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("GK", callback_data="sub_gk")],
        [InlineKeyboardButton("Math", callback_data="sub_math")],
        [InlineKeyboardButton("Reasoning", callback_data="sub_reasoning")],
        [InlineKeyboardButton("English", callback_data="sub_english")]
    ]

    await update.message.reply_text(
        "Choose Subject:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data.startswith("sub_"):
        subject = data.replace("sub_", "")
        question = get_question(subject)

        active_tests[user_id] = {
            "subject": subject,
            "question": question
        }

        await send_question(query.message, question)

    elif data.startswith("ans_"):
        if user_id not in active_tests:
            await query.message.reply_text("No active test.")
            return

        selected = data.replace("ans_", "")
        test_data = active_tests[user_id]
        question = test_data["question"]
        subject = test_data["subject"]

        if selected == question["answer"]:
            await query.message.reply_text("✅ Correct")
        else:
            await query.message.reply_text(
                f"❌ Wrong\nCorrect Answer: {question['answer']}"
            )

        next_question = get_question(subject)

        active_tests[user_id]["question"] = next_question

        await send_question(query.message, next_question)


async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": f"Answer this SSC exam question simply: {question}"
                }
            ],
            temperature=0.3,
            max_tokens=500
        )

        answer = response.choices[0].message.content

        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text(f"AI Error: {str(e)}")


app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("starttest", start_test))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_ai))

print("Bot running...")
app.run_polling()
