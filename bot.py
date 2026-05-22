import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

WELCOME_TEXT = """
🎓 SSC Study Assistant Bot

Ask any SSC exam related question in Hindi or English.

Examples:
भारत का संविधान कब लागू हुआ?
Percentage shortcut trick
SSC reasoning blood relation question
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send any SSC exam related question.\n\n"
        "Examples:\n"
        "भारत का संविधान कब लागू हुआ?\n"
        "LCM shortcut trick\n"
        "SSC reasoning puzzle"
    )

async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text

    await update.message.reply_text("Thinking...")

    prompt = f"""
You are an expert SSC exam teacher for Indian government exam students.

Rules:
- Answer in simple Hindi if question is Hindi.
- Answer in English if question is English.
- Focus only on SSC exam preparation.
- Give accurate explanation.
- If math, explain step by step.
- If reasoning, solve clearly.
- Keep answer student-friendly.

Question:
{user_question}
"""

    try:
        response = model.generate_content(prompt)
        answer = response.text

        if len(answer) > 4000:
            answer = answer[:4000]

        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text("Error: AI response failed. Try again.")

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_ai))

app.run_polling()
