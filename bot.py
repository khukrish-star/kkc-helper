import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8644125887
USERS_FILE = "users.json"


def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(list(users), f)


users = load_users()
broadcast_mode = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users.add(user_id)
    save_users(users)

    keyboard = [
        [InlineKeyboardButton("Help", callback_data="help")],
        [InlineKeyboardButton("My ID", callback_data="myid")],
        [InlineKeyboardButton("About", callback_data="about")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Welcome to KKC Helper Bot 🚀",
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Start bot\n"
        "/help - Help menu\n"
        "/myid - Get your Telegram ID\n"
        "/stats - Total users (admin only)\n"
        "/broadcast - Send text to all users\n"
        "/broadcastphoto - Send photo to all users\n"
        "/broadcastfile - Send file to all users\n"
        "/broadcastvideo - Send video to all users"
    )


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Your ID: {update.effective_user.id}")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Not authorized")
        return

    await update.message.reply_text(f"Total users: {len(users)}")


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Not authorized")
        return

    message = " ".join(context.args)

    if not message:
        await update.message.reply_text("Usage: /broadcast your message")
        return

    for user in users:
        try:
            await context.bot.send_message(chat_id=user, text=message)
        except:
            pass

    await update.message.reply_text("Text broadcast sent")


async def broadcast_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Not authorized")
        return

    broadcast_mode[update.effective_user.id] = "photo"
    await update.message.reply_text("Now send the photo")


async def broadcast_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Not authorized")
        return

    broadcast_mode[update.effective_user.id] = "file"
    await update.message.reply_text("Now send the file")


async def broadcast_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Not authorized")
        return

    broadcast_mode[update.effective_user.id] = "video"
    await update.message.reply_text("Now send the video")


async def media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    mode = broadcast_mode.get(update.effective_user.id)

    if mode == "photo" and update.message.photo:
        photo = update.message.photo[-1].file_id

        for user in users:
            try:
                await context.bot.send_photo(chat_id=user, photo=photo)
            except:
                pass

        broadcast_mode.pop(update.effective_user.id, None)
        await update.message.reply_text("Photo broadcast sent")

    elif mode == "file" and update.message.document:
        document = update.message.document.file_id

        for user in users:
            try:
                await context.bot.send_document(chat_id=user, document=document)
            except:
                pass

        broadcast_mode.pop(update.effective_user.id, None)
        await update.message.reply_text("File broadcast sent")

    elif mode == "video" and update.message.video:
        video = update.message.video.file_id

        for user in users:
            try:
                await context.bot.send_video(chat_id=user, video=video)
            except:
                pass

        broadcast_mode.pop(update.effective_user.id, None)
        await update.message.reply_text("Video broadcast sent")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "help":
        await query.edit_message_text("Use /help command")

    elif query.data == "myid":
        await query.edit_message_text(f"Your Telegram ID: {query.from_user.id}")

    elif query.data == "about":
        await query.edit_message_text("KKC Helper Bot v3 🚀")


app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("myid", myid))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("broadcastphoto", broadcast_photo))
app.add_handler(CommandHandler("broadcastfile", broadcast_file))
app.add_handler(CommandHandler("broadcastvideo", broadcast_video))

app.add_handler(
    MessageHandler(
        filters.PHOTO | filters.Document.ALL | filters.VIDEO,
        media_handler
    )
)

app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()
