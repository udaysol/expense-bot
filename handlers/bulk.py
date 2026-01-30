from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from database import get_connection

async def bulk_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text
    lines = text.split("\n")[1:]  # skip /bulk line

    if not lines:
        return await update.message.reply_text(
            "❌ Usage:\n/bulk\namount description [paidby=Name]"
        )

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

    # ---- Participants ----
    cur.execute(
        "SELECT name FROM participants WHERE trip_id=?",
        (trip_id,)
    )
    participants = [r[0] for r in cur.fetchall()]
    n = len(participants)

    success = 0
    failed = 0

    for line in lines:
        parts = line.strip().split()
        if len(parts) < 2:
            failed += 1
            continue

        try:
            amount = int(parts[0])
            if amount <= 0:
                raise ValueError
        except ValueError:
            failed += 1
            continue

        paid_by = update.effective_user.first_name
        desc_parts = []

        for p in parts[1:]:
            if p.startswith("paidby="):
                paid_by = p.split("=", 1)[1]
            else:
                desc_parts.append(p)

        if paid_by not in participants:
            failed += 1
            continue

        description = " ".join(desc_parts)

        base = amount // n
        rem = amount % n

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

        for i, person in enumerate(participants):
            share = base + (1 if i < rem else 0)
            cur.execute(
                """
                INSERT INTO expense_splits (expense_id, person, amount)
                VALUES (?, ?, ?)
                """,
                (expense_id, person, share)
            )

        success += 1

    conn.commit()
    conn.close()

    await update.message.reply_text(
        f"📦 Bulk add completed\n"
        f"✅ Added: {success}\n"
        f"❌ Failed: {failed}"
    )
