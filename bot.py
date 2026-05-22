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

broadcast_mode = {}
last_broadcast_messages = []


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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in users:
        return

    users.add(user_id)
    save_users(users)

    keyboard = [
        [InlineKeyboardButton("Help", callback_data="help")],
        [InlineKeyboardButton("My ID", callback_data="myid")],
        [InlineKeyboardButton("About", callback_data="about")],
    ]

    await update.message.reply_text(
        "Welcome to KKC Helper Bot 🚀",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start\n"
        "/help\n"
        "/myid\n"
        "/stats\n"
        "/broadcast your message\n"
        "/broadcastphoto\n"
        "/broadcastfile\n"
        "/broadcastvideo\n"
        "/delete_last_broadcast"
    )


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Your ID: {update.effective_user.id}")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Not authorized")
        return

    await update.message.reply_text(f"Total users: {len(users)}")


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_broadcast_messages

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Not authorized")
        return

    message = " ".join(context.args)

    if not message:
        await update.message.reply_text("Usage: /broadcast your message")
        return

    last_broadcast_messages = []

    for user in users:
        try:
            sent = await context.bot.send_message(chat_id=user, text=message)
            last_broadcast_messages.append((user, sent.message_id))
        except:
            pass

    await update.message.reply_text("Text broadcast sent")


async def broadcast_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    broadcast_mode[ADMIN_ID] = "photo"
    await update.message.reply_text("Now send photo")


async def broadcast_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    broadcast_mode[ADMIN_ID] = "file"
    await update.message.reply_text("Now send file")


async def broadcast_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    broadcast_mode[ADMIN_ID] = "video"
    await update.message.reply_text("Now send video")


async def delete_last_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_broadcast_messages

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Not authorized")
        return

    deleted = 0

    for chat_id, msg_id in last_broadcast_messages:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            deleted += 1
        except:
            pass

    last_broadcast_messages = []
    await update.message.reply_text(f"Deleted from {deleted} users")


async def media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_broadcast_messages

    if update.effective_user.id != ADMIN_ID:
        return

    mode = broadcast_mode.get(ADMIN_ID)

    if not mode:
        return

    last_broadcast_messages = []

    if mode == "photo" and update.message.photo:
        file_id = update.message.photo[-1].file_id

        for user in users:
            try:
                sent = await context.bot.send_photo(chat_id=user, photo=file_id)
                last_broadcast_messages.append((user, sent.message_id))
            except:
                pass

    elif mode == "file" and update.message.document:
        file_id = update.message.document.file_id

        for user in users:
            try:
                sent = await context.bot.send_document(chat_id=user, document=file_id)
                last_broadcast_messages.append((user, sent.message_id))
            except:
                pass

    elif mode == "video":
        file_id = None

        if update.message.video:
            file_id = update.message.video.file_id
        elif update.message.animation:
            file_id = update.message.animation.file_id
        elif update.message.document:
            file_id = update.message.document.file_id

        if file_id:
            for user in users:
                try:
                    if update.message.video:
                        sent = await context.bot.send_video(chat_id=user, video=file_id)
                    elif update.message.animation:
                        sent = await context.bot.send_animation(chat_id=user, animation=file_id)
                    else:
                        sent = await context.bot.send_document(chat_id=user, document=file_id)

                    last_broadcast_messages.append((user, sent.message_id))
                except:
                    pass

    broadcast_mode.pop(ADMIN_ID, None)
    await update.message.reply_text("Broadcast sent")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "help":
        await query.edit_message_text("Use /help")
    elif query.data == "myid":
        await query.edit_message_text(f"Your ID: {query.from_user.id}")
    elif query.data == "about":
        await query.edit_message_text("KKC Helper Bot 🚀")


app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("myid", myid))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("broadcastphoto", broadcast_photo))
app.add_handler(CommandHandler("broadcastfile", broadcast_file))
app.add_handler(CommandHandler("broadcastvideo", broadcast_video))
app.add_handler(CommandHandler("delete_last_broadcast", delete_last_broadcast))

app.add_handler(
    MessageHandler(
        filters.PHOTO | filters.Document.ALL | filters.VIDEO | filters.ANIMATION,
        media_handler
    )
)

app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()
