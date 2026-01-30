from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from database import get_connection

async def add_personal_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message = update.message.text
    args = context.args

    if not args:
        return await update.message.reply_text(
            "❌ Usage:\n/addp Description paidby=Name ..."
        )

    description = args[0]
    paid_by = update.effective_user.first_name

    # ---- Parse paidby if present ----
    for arg in args[1:]:
        if arg.startswith("paidby="):
            paid_by = arg.split("=", 1)[1]

    # ---- Get active trip ----
    conn = get_connection()
    cur = conn.cursor()

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

    # ---- Parse personal splits ----
    splits = {}

    lines = message.split("\n")[1:]
    if lines:
        for line in lines:
            parts = line.strip().split()
            if len(parts) != 2:
                continue
            name, amt = parts
            if not amt.isdigit():
                continue
            splits[name] = int(amt)
    else:
        for arg in args[1:]:
            if "=" in arg and not arg.startswith("paidby="):
                name, amt = arg.split("=", 1)
                if amt.isdigit():
                    splits[name] = int(amt)

    if not splits:
        conn.close()
        return await update.message.reply_text(
            "❌ No valid personal splits found."
        )

    # ---- Validate splits ----
    for name in splits:
        if name not in participants:
            conn.close()
            return await update.message.reply_text(
                f"❌ '{name}' is not a participant."
            )

    total_amount = sum(splits.values())

    # ---- Insert expense ----
    cur.execute(
        """
        INSERT INTO expenses
        (trip_id, description, total_amount, paid_by, split_type, timestamp)
        VALUES (?, ?, ?, ?, 'uneven', ?)
        """,
        (trip_id, description, total_amount, paid_by, datetime.now().isoformat())
    )
    expense_id = cur.lastrowid

    # ---- Insert splits ----
    for name, amt in splits.items():
        cur.execute(
            """
            INSERT INTO expense_splits (expense_id, person, amount)
            VALUES (?, ?, ?)
            """,
            (expense_id, name, amt)
        )

    conn.commit()
    conn.close()

    await update.message.reply_text(
        f"✅ Uneven expense added\n"
        f"💸 {description}\n"
        f"₹{total_amount} paid by {paid_by}"
    )
