from telegram import Update
from telegram.ext import ContextTypes
from database import get_connection
from datetime import datetime

from services.export import export_trip_to_excel

async def end_trip(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        return await update.message.reply_text("❌ No active trip found.")

    trip_id, trip_name = row

    # ---- Get participants ----
    cur.execute(
        "SELECT name FROM participants WHERE trip_id=?",
        (trip_id,)
    )
    participants = [r[0] for r in cur.fetchall()]

    balances = {name: 0 for name in participants}

    # ---- Process expenses ----
    cur.execute(
        "SELECT id, total_amount, paid_by FROM expenses WHERE trip_id=?",
        (trip_id,)
    )
    expenses = cur.fetchall()

    for expense_id, total, paid_by in expenses:
        balances[paid_by] += total

        cur.execute(
            "SELECT person, amount FROM expense_splits WHERE expense_id=?",
            (expense_id,)
        )
        for person, amount in cur.fetchall():
            balances[person] -= amount

    # ---- Settlement calculation ----
    receivers = []
    payers = []

    for person, balance in balances.items():
        if balance > 0:
            receivers.append([person, balance])
        elif balance < 0:
            payers.append([person, -balance])

    settlements = []
    i = j = 0

    while i < len(payers) and j < len(receivers):
        payer, owe = payers[i]
        receiver, receive = receivers[j]

        amount = min(owe, receive)
        settlements.append((payer, receiver, amount))

        payers[i][1] -= amount
        receivers[j][1] -= amount

        if payers[i][1] == 0:
            i += 1
        if receivers[j][1] == 0:
            j += 1

    # ---- Close trip ----
    cur.execute(
        "UPDATE trips SET is_active=0, end_time=? WHERE id=?",
        (datetime.now().isoformat(), trip_id)
    )

    conn.commit()
    conn.close()

    total_trip_expense = sum(
        total for _, total, _ in expenses
    )

    # ---- Build response ----
    msg = (
        f"🏁 Trip '{trip_name}' ended\n\n"
        f"💸 Total Trip Expense: ₹{total_trip_expense}\n\n"
        f"💰 Settlement:\n"
    )

    if not settlements:
        msg += "Everyone is settled up 🎉"
    else:
        for payer, receiver, amount in settlements:
            msg += f"{payer} → pays ₹{amount} to {receiver}\n"

    # Save Excel sheet
    file_name = f"{trip_name}_expenses.xlsx"
    export_trip_to_excel(trip_id, trip_name, file_name)

    await update.message.reply_document(
        document=open(file_name, "rb"),
        filename=file_name
    )


    await update.message.reply_text(msg)
