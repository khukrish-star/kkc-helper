import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

WELCOME_TEXT = """
🎓 SSC Study Assistant Bot

SSC preparation assistant.

Hindi + English supported.

Examples:
भारत का संविधान कब लागू हुआ?
Percentage shortcut trick
Blood relation reasoning question
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ask any SSC related question.\n\n"
        "Examples:\n"
        "भारत का संविधान कब लागू हुआ?\n"
        "LCM shortcut trick\n"
        "Reasoning puzzle"
    )

async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text

    wait_msg = await update.message.reply_text("Thinking...")

    prompt = f"""
You are an expert SSC exam teacher for Indian government exam students.

Rules:
1. If user asks in Hindi, answer in Hindi.
2. If user asks in English, answer in English.
3. Focus on SSC exam level explanations.
4. Explain clearly and simply.
5. If math, solve step by step.
6. If reasoning, explain logic.
7. Keep answers accurate.

Question:
{question}
"""

    try:
        response = model.generate_content(prompt)
        answer = response.text

        if len(answer) > 4000:
            answer = answer[:4000]

        await wait_msg.edit_text(answer)

    except Exception:
        await wait_msg.edit_text("AI error. Try again.")

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_ai))

app.run_polling()
