import os
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
    await update.message.reply_text(
        "🎓 Welcome to KKC Helper Bot\n\n"
        "SSC preparation assistant.\n"
        "Commands:\n"
        "/help - Help\n"
        "/starttest - Mock Test\n"
        "/schedule - Daily schedule"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n"
        "/start → Start bot\n"
        "/help → Help\n"
        "/starttest → Mock test\n"
        "/schedule → Daily auto test schedule\n\n"
        "Ask SSC doubts directly:\n"
        "भारत का संविधान कब लागू हुआ?\n"
        "Percentage shortcut trick\n"
        "Coding decoding question"
    )


async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📅 Daily Auto Test Schedule\n\n"
        "📝 SSC CGL → 07:00\n"
        "📝 SSC CPO → 11:00\n"
        "📝 SSC CHSL → 15:00\n"
        "📝 SSC MTS → 19:00\n"
        "📝 SSC GD → 21:00"
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


async def send_question(query, user_id, context):
    test = active_tests[user_id]

    if test["current"] >= len(test["questions"]):
        await finish_test(query, user_id, context)
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

    text = (
        f"Q{test['current'] + 1}/{len(test['questions'])}\n\n"
        f"📘 Topic: {q['topic']}\n"
        f"🏆 Likely Exam: {q['exam']} {q['year']}\n\n"
        f"{q['question']}\n\n"
        f"A) {q['options']['A']}\n"
        f"B) {q['options']['B']}\n"
        f"C) {q['options']['C']}\n"
        f"D) {q['options']['D']}"
    )

    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def finish_test(query, user_id, context):
    test = active_tests[user_id]

    total = len(test["questions"])
    correct = test["correct"]
    wrong = test["wrong"]
    score = test["score"]

    accuracy = (correct / total) * 100 if total > 0 else 0

    msg = (
        "✅ TEST COMPLETED\n\n"
        f"📊 Score: {score}\n"
        f"✅ Correct: {correct}\n"
        f"❌ Wrong: {wrong}\n"
        f"🎯 Accuracy: {accuracy:.1f}%"
    )

    await query.message.reply_text(msg)

    del active_tests[user_id]


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data.startswith("subject_"):
        subject = query.data.replace("subject_", "")

        questions = generate_mock_test(subject, 8)

        active_tests[user_id] = {
            "questions": questions,
            "current": 0,
            "score": 0,
            "correct": 0,
            "wrong": 0,
        }

        await send_question(query, user_id, context)

    elif query.data.startswith("ans_"):
        selected = query.data.replace("ans_", "")
        test = active_tests[user_id]
        q = test["questions"][test["current"]]

        if selected == q["answer"]:
            test["score"] += 2
            test["correct"] += 1
        else:
            test["score"] -= 0.5
            test["wrong"] += 1

        test["current"] += 1

        await send_question(query, user_id, context)


async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text

    try:
        answer = ask_ssc_ai(question, "Hindi")
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text(f"AI Error: {str(e)}")


BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("schedule", schedule))
app.add_handler(CommandHandler("starttest", start_test))
app.add_handler(CallbackQueryHandler(button_handler))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        ask_ai
    )
)

print("KKC Bot running...")
app.run_polling()
