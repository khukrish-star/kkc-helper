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

# safer model
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
3. Focus only on SSC exam level preparation.
4. Explain clearly and simply.
5. If math, solve step by step.
6. If reasoning, explain logic.
7. Keep answers accurate and exam-focused.
8. Keep response concise but useful.

Question:
{question}
"""

    try:
        response = model.generate_content(prompt)
        answer = response.text

        if len(answer) > 4000:
            answer = answer[:4000]

        await wait_msg.edit_text(answer)

    except Exception as e:
        error_text = str(e)

        if "429" in error_text:
            await wait_msg.edit_text(
                "AI usage limit reached. Try again after some time or enable billing in Gemini API."
            )
        else:
            await wait_msg.edit_text(
                f"AI Error:\n{error_text[:500]}"
            )

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_ai))

print("Bot started...")
app.run_polling()
