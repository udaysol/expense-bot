from telegram import Update
from telegram.ext import ContextTypes
from database import get_connection

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    conn = get_connection()
    cur = conn.cursor()

    # ---- Get active trip ----
    cur.execute(
        "SELECT id, trip_name FROM trips WHERE chat_id=? AND is_active=1",
        (chat_id,)
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        return await update.message.reply_text("❌ No active trip.")

    trip_id, trip_name = row

    # ---- Get participants ----
    cur.execute(
        "SELECT name FROM participants WHERE trip_id=?",
        (trip_id,)
    )
    participants = [r[0] for r in cur.fetchall()]

    balances = {name: 0 for name in participants}
    total_spent = 0

    # ---- Process expenses ----
    cur.execute(
        "SELECT id, total_amount, paid_by FROM expenses WHERE trip_id=?",
        (trip_id,)
    )
    expenses = cur.fetchall()

    for expense_id, total, paid_by in expenses:
        total_spent += total
        balances[paid_by] += total

        cur.execute(
            "SELECT person, amount FROM expense_splits WHERE expense_id=?",
            (expense_id,)
        )
        for person, amount in cur.fetchall():
            balances[person] -= amount

    conn.close()

    # ---- Build message ----
    msg = (
        f"📍 Active Trip: {trip_name}\n\n"
        f"👥 Participants ({len(participants)}):\n"
        f"{', '.join(participants)}\n\n"
        f"💸 Total spent so far: ₹{total_spent}\n\n"
        f"💰 Current balances:\n"
    )

    for person, balance in balances.items():
        sign = "+" if balance >= 0 else "-"
        msg += f"{person}: {sign}₹{abs(balance)}\n"

    await update.message.reply_text(msg)
