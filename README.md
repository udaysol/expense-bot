# Trip Expense Tracker Telegram Bot

A **Telegram group bot** to track trip expenses, handle uneven splits, support multiple payers, undo mistakes, and generate a **clean Excel report** at the end of the trip.

Built for real trips with friends — simple to use, accurate, and human-readable.

---

## Features

### Trip Management
- Start a trip with named participants
- Add members mid-trip (no retroactive charges)
- One active trip per group

### Expense Tracking
- Even split expenses (with safe rounding)
- Uneven / personal split expenses (combo meals)
- Multiple payers supported
- No floating-point errors

### Safety & Visibility
- Undo last **3 expenses**
- Live `/status` showing balances
- Server restarts do **not** lose trip data

### Reporting
- Generates a **polished Excel spreadsheet** on `/end`
- Human-friendly layout (one row per expense)
- Per-person columns
- Color-coded balances
- Total trip expense included
- Final settlement (who pays whom)

---

## Tech Stack

- **Python**
- **python-telegram-bot**
- **SQLite** (persistent storage)
- **pandas + openpyxl** (Excel export)

---

## 📁 Project Structure
```bash
 expense-bot/
├──  bot.py
├──  config.py
├──  data
│   └──  expenses.db
├──  database.py
├──  folder_structure.md
├──  handlers
│   ├──  add_expense.py
│   ├──  add_member.py
│   ├──  add_personal_expense.py
│   ├──  bulk.py
│   ├──  end_trip.py
│   ├──  start_trip.py
│   ├──  status.py
│   └──  undo.py
├──  LICENSE
├── 󰂺 README.md
├──  requirements.txt
└──  services
    └──  export.py
```


---

## Bot Commands

### `/start`
Start a new trip.

```
/start GoaTrip John Doe Jack
```

---

### `/add`
Add an **even split** expense.

```
/add 1200 Dinner
/add 900 Petrol paidby=Jack
```

✔ Automatically rounds when not perfectly divisible.

---

### `/addp`
Add an **uneven / personal split** expense.

Multi-line (recommended):
```
/addp Dinner paidby=Jack
John 450
Jack 350
Doe 400
```

Single-line:
```
/addp Lunch paidby=John John=200 Jack=150 Doe=250
```

---

### `/addmember`
Add a new participant mid-trip.
```
/addmember Jill
```

New member is included **only in future expenses**.

---

### `/status`
View live trip summary.
```
/status
```

Shows:
- Participants
- Total spent so far
- Current balances

---

### `/undo`
Undo the **last expense** (up to last 3).
```
/undo
```

Safe — recalculates balances automatically.

---

### `/end`
End the trip and generate final report.

```
/end
```

Outputs:
- Total trip expense
- Settlement (who pays whom)
- Excel file download 📎

---

## Excel Report (Generated on `/end`)

### Sheet 1 — Expense Log
- One row per expense
- One column per person
- Total trip expense at bottom

### Sheet 2 — Person Summary
- Total paid
- Total owes
- Net balance (color-coded)

### Sheet 3 — Settlement
- Final minimal transactions

---

## Deployment

The bot is designed to run as a **long-polling process**.

### Recommended (Free, No Card)
- Railway (background worker)

### Environment Variables
`BOT_TOKEN=<your_telegram_bot_token>`


Start command:
```bash
python bot.py
```
