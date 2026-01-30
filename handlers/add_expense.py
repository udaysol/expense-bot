from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from database import get_connection

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    args = context.args

    if len(args) < 2:
        return await update.message.reply_text(
            "❌ Usage:\n/add amount description [paidby=Name]"
        )

    # ---- Parse amount ----
    try:
        amount = int(args[0])
        if amount <= 0:
            raise ValueError
    except ValueError:
        return await update.message.reply_text("❌ Amount must be a positive number.")

    # ---- Parse description & paidby ----
    paid_by = update.effective_user.first_name
    description_parts = []

    for arg in args[1:]:
        if arg.startswith("paidby="):
            paid_by = arg.split("=", 1)[1]
        else:
            description_parts.append(arg)

    description = " ".join(description_parts)

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
        return await update.message.reply_text("❌ No active trip found.")

    trip_id = row[0]

    # ---- Get participants ----
    cur.execute(
        "SELECT name FROM participants WHERE trip_id=?",
        (trip_id,)
    )
    participants = [r[0] for r in cur.fetchall()]

    if paid_by not in participants:
        conn.close()
        return await update.message.reply_text(
            f"❌ '{paid_by}' is not a participant."
        )

    num_people = len(participants)
    base_share = amount // num_people
    remainder = amount % num_people

    # ---- Insert expense ----
    cur.execute(
        """
        INSERT INTO expenses
        (trip_id, description, total_amount, paid_by, split_type, timestamp)
        VALUES (?, ?, ?, ?, 'even', ?)
        """,
        (trip_id, description, amount, paid_by, datetime.now().isoformat())
    )
    expense_id = cur.lastrowid

    # ---- Insert splits ----
    for i, person in enumerate(participants):
        share = base_share
        if i < remainder:
            share += 1

        cur.execute(
            """
            INSERT INTO expense_splits (expense_id, person, amount)
            VALUES (?, ?, ?)
            """,
            (expense_id, person, share)
        )

    conn.commit()
    conn.close()

    await update.message.reply_text(
        f"✅ Expense added\n"
        f"💸 {description}\n"
        f"₹{amount} paid by {paid_by}\n"
        f"Split approx ₹{base_share} each"
    )
