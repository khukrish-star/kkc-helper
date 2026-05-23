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

from ai_helper import ask_ssc_ai, generate_mock_questions
from mock_engine import (
    start_mock,
    get_current_question,
    submit_answer,
    is_test_finished,
    finish_mock,
)
from database import add_user, update_last_active
from scheduler import format_schedule_message

BOT_TOKEN = os.getenv("BOT_TOKEN")


WELCOME_TEXT = """
🎓 KKC Helper Bot

Features:
✅ SSC AI Doubt Solver
✅ Realistic Mock Tests
✅ Weak Topic Analysis
✅ Performance Tracking
✅ Daily Exam Schedule

Commands:
/start
/help
/starttest
/schedule
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    add_user(
        user.id,
        user.username or "",
        user.full_name
    )

    await update.message.reply_text(WELCOME_TEXT)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """
Commands:

/start → Start bot
/help → Help
/starttest → Mock test
/schedule → Daily auto test schedule

Ask SSC doubts directly:
भारत का संविधान कब लागू हुआ?
Percentage shortcut trick
Coding decoding question
"""
    )


async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(format_schedule_message())


async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    update_last_active(user.id)

    question = update.message.text

    wait_msg = await update.message.reply_text("Thinking...")

    try:
        answer = ask_ssc_ai(question)
        await wait_msg.edit_text(answer[:4000])

    except Exception as e:
        await wait_msg.edit_text(f"Error: {str(e)}")


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
    q = get_current_question(user_id)

    if not q:
        result = finish_mock(user_id)

        weak_text = "None"

        if result["weak_topics"]:
            weak_text = "\n".join(
                [f"• {k}: {v}" for k, v in result["weak_topics"].items()]
            )

        text = f"""
✅ TEST COMPLETED

📊 Score: {result['score']} / {result['total_marks']}
✅ Correct: {result['correct']}
❌ Wrong: {result['wrong']}
🎯 Accuracy: {result['accuracy']}%
⏱ Time Taken: {result['time_taken']}

📉 Weak Topics:
{weak_text}
"""

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=text
        )
        return

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
📘 Topic: {q['topic']}

{q['question']}

A) {q['options']['A']}
B) {q['options']['B']}
C) {q['options']['C']}
D) {q['options']['D']}
"""

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data.startswith("subject_"):
        subject = query.data.replace("subject_", "")

        await query.edit_message_text("Generating mock test...")

        questions = generate_mock_questions(
            subject=subject,
            count=10,
            language="English"
        )

        start_mock(
            user_id=user_id,
            questions=questions,
            exam_type="SSC MOCK",
            subject=subject,
            language="English"
        )

        await send_question(query, user_id, context)

    elif query.data.startswith("ans_"):
        selected = query.data.replace("ans_", "")

        submit_answer(
            user_id,
            selected,
            negative_marking=0.5
        )

        await send_question(query, user_id, context)


app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("starttest", start_test))
app.add_handler(CommandHandler("schedule", schedule_command))

app.add_handler(CallbackQueryHandler(button_handler))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        ask_ai
    )
)

print("KKC Helper Bot Running...")
app.run_polling()
