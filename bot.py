import os
from groq import Groq
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

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

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert SSC exam teacher for Indian students.

Rules:
1. If user asks in Hindi, answer in Hindi.
2. If user asks in English, answer in English.
3. Focus only on SSC exam related study help.
4. Explain clearly and simply.
5. If math, solve step by step.
6. If reasoning, explain logic.
7. Keep answers accurate and short."""
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=0.4,
            max_tokens=1200
        )

        answer = response.choices[0].message.content

        if len(answer) > 4000:
            answer = answer[:4000]

        await wait_msg.edit_text(answer)

    except Exception as e:
        await wait_msg.edit_text(f"AI Error:\n{str(e)}")

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_ai))

print("Bot running...")
app.run_polling()
