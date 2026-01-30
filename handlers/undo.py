from telegram import Update
from telegram.ext import ContextTypes
from database import get_connection

async def undo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

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

    # ---- Get last 3 expenses ----
    cur.execute(
        """
        SELECT id, description, total_amount, paid_by
        FROM expenses
        WHERE trip_id=?
        ORDER BY timestamp DESC
        LIMIT 3
        """,
        (trip_id,)
    )
    expenses = cur.fetchall()

    if not expenses:
        conn.close()
        return await update.message.reply_text("❌ Nothing to undo.")

    # ---- Pick most recent ----
    expense_id, desc, total, paid_by = expenses[0]

    # ---- Delete splits first ----
    cur.execute(
        "DELETE FROM expense_splits WHERE expense_id=?",
        (expense_id,)
    )

    # ---- Delete expense ----
    cur.execute(
        "DELETE FROM expenses WHERE id=?",
        (expense_id,)
    )

    conn.commit()
    conn.close()

    await update.message.reply_text(
        f"↩️ Undone last expense:\n"
        f"💸 {desc}\n"
        f"₹{total} paid by {paid_by}"
    )
