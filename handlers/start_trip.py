from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from database import get_connection

async def start_trip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    args = context.args

    if len(args) < 3:
        return await update.message.reply_text(
            "❌ Usage:\n/start TripName Person1 Person2 ..."
        )

    trip_name = args[0]
    participants = args[1:]

    if len(set(participants)) != len(participants):
        return await update.message.reply_text(
            "❌ Participant names must be unique."
        )

    conn = get_connection()
    cur = conn.cursor()

    # Check active trip
    cur.execute(
        "SELECT id FROM trips WHERE chat_id=? AND is_active=1",
        (chat_id,)
    )
    if cur.fetchone():
        conn.close()
        return await update.message.reply_text(
            "❌ A trip is already active in this group."
        )

    # Create trip
    cur.execute(
        """
        INSERT INTO trips (chat_id, trip_name, is_active, start_time)
        VALUES (?, ?, 1, ?)
        """,
        (chat_id, trip_name, datetime.now().isoformat())
    )
    trip_id = cur.lastrowid

    # Insert participants
    for name in participants:
        cur.execute(
            "INSERT INTO participants (trip_id, name) VALUES (?, ?)",
            (trip_id, name)
        )

    conn.commit()
    conn.close()

    await update.message.reply_text(
        f"🏝 Trip '{trip_name}' started!\n"
        f"👥 Participants: {', '.join(participants)}"
    )
