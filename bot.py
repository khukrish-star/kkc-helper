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

# FIXED MODEL
model = genai.GenerativeModel("gemini-1.5-flash-latest")

WELCOME_TEXT = """
🎓 SSC Study Assistant Bot

SSC preparation assistant for:
SSC CGL
SSC CHSL
SSC MTS
SSC GD
SSC CPO
SSC Stenographer

Hindi + English supported.

Examples:
भारत का संविधान कब लागू हुआ?
Percentage shortcut trick
Blood relation reasoning question
LCM shortcut trick
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """
Ask any SSC related question.

Examples:
भारत का संविधान कब लागू हुआ?
LCM shortcut trick
Reasoning puzzle
Percentage shortcut
English grammar rules
GK question
"""
    )

async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text

    wait_msg = await update.message.reply_text("Thinking...")

    prompt = f"""
You are India's expert SSC exam teacher.

Rules:
1. Answer only SSC exam related questions.
2. If user asks in Hindi, reply in Hindi.
3. If user asks in English, reply in English.
4. Explain simply like a teacher.
5. For maths, solve step by step.
6. For reasoning, explain logic clearly.
7. For GK/history/polity, give accurate answer.
8. If question is not SSC related, politely refuse.
9. Keep answer useful for exam preparation.

User Question:
{question}
"""

    try:
        response = model.generate_content(prompt)
        answer = response.text

        if len(answer) > 4000:
            answer = answer[:4000]

        await wait_msg.edit_text(answer)

    except Exception as e:
        await wait_msg.edit_text(f"AI Error:\n{str(e)}")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Unknown command. Use /help")

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_ai))
app.add_handler(MessageHandler(filters.COMMAND, unknown))

print("Bot started...")
app.run_polling()
