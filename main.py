import logging
import asyncio
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# -------------------------------
# Fixed Config (Secrets here)
# -------------------------------
TOKEN = "8380050511:AAHCU4h9lNDkQJMzU44kxE3Nx-Ujm6JTq2c"
OWNER_ID = 6091430516
REF_LINK = "https://dkwin9.com/#/register?invitationCode=16532572738"

# -------------------------------
# Logger Setup
# -------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# -------------------------------
# Global Variables
# -------------------------------
signal_running = False
current_chat_id = None
preyod_number = 1  # Market period number
last_number = None

# -------------------------------
# Commands
# -------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"ðŸ¤– SHAHED AI PREDICTION BOT\n\n"
        f"ðŸ”¹ Auto signal bot for DK WIN\n"
        f"ðŸ”¹ Owner: @shahedbintarek\n"
        f"ðŸ”¹ Join via link: {REF_LINK}\n\n"
        f"Commands:\n"
        f"/signal_on - Start auto signals in this group\n"
        f"/signal_off - Stop auto signals"
    )

async def signal_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global signal_running, current_chat_id
    signal_running = True
    current_chat_id = update.effective_chat.id
    await update.message.reply_text("âœ… Auto Signal Started")
    asyncio.create_task(auto_signal(context))

async def signal_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global signal_running
    signal_running = False
    await update.message.reply_text("ðŸ›‘ Auto Signal Stopped")

# -------------------------------
# Signal System
# -------------------------------
async def auto_signal(context: ContextTypes.DEFAULT_TYPE):
    global signal_running, current_chat_id
    while signal_running and current_chat_id:
        await send_signal(current_chat_id, context)
        await asyncio.sleep(60)  # à¦ªà§à¦°à¦¤à¦¿ à§§ à¦®à¦¿à¦¨à¦¿à¦Ÿà§‡ à¦¨à¦¤à§à¦¨ signal

async def send_signal(chat_id, context: ContextTypes.DEFAULT_TYPE):
    global preyod_number, last_number

    # Random number generate
    number = random.randint(0, 9)
    last_number = number

    # Small/Big logic
    bet = "SMALL" if number % 2 == 1 else "BIG"

    message = (
        f"ðŸ“Š SHAHED AI PREDICTION BOT\n\n"
        f"Preyod number - {preyod_number}\n"
        f"BET - {bet}\n"
        f"Number - {number}\n"
        f"Maintain - 8 level\n\n"
        f"ðŸ”¹ Join - {REF_LINK}"
    )

    await context.bot.send_message(chat_id=chat_id, text=message)
    preyod_number += 1  # Market period auto increase

# -------------------------------
# Main Runner
# -------------------------------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal_on", signal_on))
    app.add_handler(CommandHandler("signal_off", signal_off))

    print("âœ… SHAHED AI Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
