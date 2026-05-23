import os
import traceback
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from ai_helper import ask_ssc_ai
from mock_engine import generate_mock_test

active_tests = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("KKC Helper Bot Active ✅")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start\n"
        "/help\n"
        "/starttest\n"
        "/schedule\n\n"
        "Ask any SSC question directly."
    )


async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "SSC CGL → 07:00\n"
        "SSC CPO → 11:00\n"
        "SSC CHSL → 15:00\n"
        "SSC MTS → 19:00\n"
        "SSC GD → 21:00"
    )


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


async def send_question(query, user_id):
    test = active_tests[user_id]

    if test["current"] >= len(test["questions"]):
        await finish_test(query, user_id)
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
        ]
    ]

    text = f"""
Q{test['current'] + 1}/{len(test['questions'])}

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


async def finish_test(query, user_id):
    test = active_tests[user_id]

    await query.message.reply_text(
        f"Test Complete ✅\n"
        f"Score: {test['score']}\n"
        f"Correct: {test['correct']}\n"
        f"Wrong: {test['wrong']}"
    )

    del active_tests[user_id]


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data.startswith("subject_"):
        subject = query.data.replace("subject_", "")
        questions = generate_mock_test(subject, 5)

        active_tests[user_id] = {
            "questions": questions,
            "current": 0,
            "score": 0,
            "correct": 0,
            "wrong": 0
        }

        await send_question(query, user_id)

    elif query.data.startswith("ans_"):
        selected = query.data.replace("ans_", "")
        test = active_tests[user_id]
        q = test["questions"][test["current"]]

        if selected == q["answer"]:
            test["score"] += 2
            test["correct"] += 1
        else:
            test["wrong"] += 1

        test["current"] += 1
        await send_question(query, user_id)


async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text

    try:
        answer = ask_ssc_ai(question, "Hindi")
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text("AI failed.")
        print(traceback.format_exc())


BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("schedule", schedule))
app.add_handler(CommandHandler("starttest", start_test))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_ai))

print("Bot running...")
app.run_polling()
