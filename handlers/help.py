from telegram import Update
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Trip Expense Tracker — Help\n\n"
        "🧳 Start a trip:\n"
        "/start TripName Person1 Person2 ...\n\n"
        "💸 Add an even split expense:\n"
        "/add Amount Description\n"
        "/add Amount Description paidby=Name\n\n"
        "🍽 Add an uneven / personal split:\n"
        "/addp Description paidby=Name\n"
        "Person1 Amount\n"
        "Person2 Amount\n\n"
        "👤 Add a new member mid-trip:\n"
        "/addmember Name\n\n"
        "📊 Check current status:\n"
        "/status\n\n"
        "↩️ Undo last expense (up to 3):\n"
        "/undo\n\n"
        "🏁 End trip & get Excel report:\n"
        "/end\n\n"
        "Tip: Type / in the chat to see all commands.\n"
        "I’ll handle the math so you can enjoy the trip 😄"
    )
