from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from config import BOT_TOKEN
from database import init_db

from handlers.start_trip import start_trip
from handlers.add_expense import add_expense
from handlers.add_personal_expense import add_personal_expense
from handlers.end_trip import end_trip
from handlers.status import status
from handlers.undo import undo
from handlers.add_member import add_member
from handlers.bulk import bulk_add

# ---- Utility: group-only check ----
def is_group(update: Update) -> bool:
    return update.effective_chat.type in ("group", "supergroup")


# ---- Fallback for private chats ----
async def private_chat_block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ This bot works only in group chats."
    )


# # ---- Placeholder handlers (we'll fill later) ----
# async def start_trip(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if not is_group(update):
#         return await private_chat_block(update, context)

#     await update.message.reply_text(
#         "🛠 Trip start command received (logic coming next)"
#     )


# async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if not is_group(update):
#         return await private_chat_block(update, context)

#     await update.message.reply_text(
#         "🛠 Add expense command received (logic coming next)"
#     )


# async def add_personal_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if not is_group(update):
#         return await private_chat_block(update, context)

#     await update.message.reply_text(
#         "🛠 Uneven expense command received (logic coming next)"
#     )


# async def end_trip(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if not is_group(update):
#         return await private_chat_block(update, context)

#     await update.message.reply_text(
#         "🛠 End trip command received (logic coming next)"
#     )
    

# ---- Main entry point ----
def main():
    # Initialize DB (safe to call every time)
    init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command routing
    app.add_handler(CommandHandler("start", start_trip))
    app.add_handler(CommandHandler("add", add_expense))
    app.add_handler(CommandHandler("addp", add_personal_expense))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("undo", undo))
    app.add_handler(CommandHandler("add_member", add_member))
    app.add_handler(CommandHandler("bulk", bulk_add))
    app.add_handler(CommandHandler("end", end_trip))

    print("🤖 Bot is running...")
    app.run_polling(poll_interval=2)


if __name__ == "__main__":
    main()
