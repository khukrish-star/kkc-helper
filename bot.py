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

# WORKING MODEL
model = genai.GenerativeModel("gemini-2.0-flash")

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
You are an expert SSC exam teacher.

Rules:
- Answer in Hindi if user asks Hindi
- Answer in English if user asks English
- Explain clearly
- Solve maths step by step
- Explain reasoning logic
- Focus only SSC level

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
        await wait_msg.edit_text(f"AI Error:\n{str(e)}")

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_ai))

print("Bot started...")
app.run_polling()
