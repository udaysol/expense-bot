from telegram import Update
from telegram.ext import ContextTypes
from database import get_connection

async def add_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    args = context.args

    if len(args) != 1:
        return await update.message.reply_text(
            "❌ Usage:\n/addmember Name"
        )

    new_member = args[0]

    conn = get_connection()
    cur = conn.cursor()

    # ---- Get active trip ----
    cur.execute(
        "SELECT id FROM trips WHERE chat_id=? AND is_active=1",
        (chat_id,)
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        return await update.message.reply_text("❌ No active trip.")

    trip_id = row[0]

    # ---- Check if already exists ----
    cur.execute(
        "SELECT 1 FROM participants WHERE trip_id=? AND name=?",
        (trip_id, new_member)
    )
    if cur.fetchone():
        conn.close()
        return await update.message.reply_text(
            f"❌ '{new_member}' is already a participant."
        )

    # ---- Add participant ----
    cur.execute(
        "INSERT INTO participants (trip_id, name) VALUES (?, ?)",
        (trip_id, new_member)
    )

    conn.commit()
    conn.close()

    await update.message.reply_text(
        f"👋 {new_member} added to the trip.\n"
        f"They will be included in expenses from now onwards."
    )
