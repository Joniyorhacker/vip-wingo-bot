import logging
import asyncio
import random
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ==== CONFIG ====
TOKEN = "8380050511:AAHCU4h9lNDkQJMzU44kxE3Nx-Ujm6JTq2c"
OWNER_ID = 6091430516
REF_LINK = "https://dkwin9.com/#/register?invitationCode=16532572738"
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M.json"

# ==== LOGGING ====
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

signal_running = False

# ==== GET LIVE PREYOD NUMBER ====
def get_market_data():
    """Fetch Real Preyod Number from API"""
    try:
        r = requests.get(API_URL, timeout=5)
        data = r.json()
        current = data.get("current", {})
        return current.get("issueNumber")
    except Exception as e:
        print("API Error:", e)
        return None

# ==== COMMANDS ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        await update.message.reply_text(
            f"🤖 𝑺𝑯𝑨𝑯𝑬𝑫 𝑨𝑰 𝑷𝑹𝑬𝑫𝑰𝑪𝑻𝑰𝑶𝑵\n\n"
            f"🔹 Auto Wingo 1 Min Signals\n"
            f"🔹 Owner: @shahedbintarek\n\n"
            f"/signal_on - Start auto signals\n"
            f"/signal_off - Stop auto signals"
        )
    else:
        await update.message.reply_text(
            f"🤖 𝑺𝑯𝑨𝑯𝑬𝑫 𝑨𝑰 𝑷𝑹𝑬𝑫𝑰𝑪𝑻𝑰𝑶𝑵\n\n"
            f"👉 Join here: {REF_LINK}"
        )

async def signal_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global signal_running
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("❌ Only owner can start signals")

    signal_running = True
    await update.message.reply_text("✅ Auto Signal Started (Debug Mode)")

    # Debug: show API response
    try:
        r = requests.get(API_URL, timeout=5)
        await context.bot.send_message(chat_id=OWNER_ID, text=f"API Response:\n{r.text[:400]}...")
    except Exception as e:
        await context.bot.send_message(chat_id=OWNER_ID, text=f"Error fetching API: {e}")

    asyncio.create_task(auto_signal(context))

async def signal_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global signal_running
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("❌ Only owner can stop signals")

    signal_running = False
    await update.message.reply_text("🛑 Auto Signal Stopped")

# ==== SEND SIGNAL ====
async def send_signal(context: ContextTypes.DEFAULT_TYPE):
    preyod_number = get_market_data()
    if not preyod_number:
        await context.bot.send_message(chat_id=OWNER_ID, text="⚠️ API Error - Preyod Number Missing")
        return

    number = random.randint(0, 9)
    bet = "SMALL" if number % 2 == 1 else "BIG"

    message = (
        f"📊 𝑺𝑯𝑨𝑯𝑬𝑫 𝑨𝑰 𝑷𝑹𝑬𝑫𝑰𝑪𝑻𝑰𝑶𝑵\n\n"
        f"Preyod number - {preyod_number}\n"
        f"BET - {bet}\n"
        f"Number - {number}\n"
        f"Maintain - 7/8 Step\n\n"
        f"🔹 Join - {REF_LINK}\n\n"
        f"Owner - @shahedbintarek"
    )
    await context.bot.send_message(chat_id=OWNER_ID, text=message)

# ==== AUTO SIGNAL LOOP ====
async def auto_signal(context: ContextTypes.DEFAULT_TYPE):
    global signal_running
    while signal_running:
        await send_signal(context)
        await asyncio.sleep(60)  # Wingo 1 Minute

# ==== MAIN ====
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal_on", signal_on))
    app.add_handler(CommandHandler("signal_off", signal_off))
    print("✅ SHAHED AI Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
