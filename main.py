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
target_chat_id = None   # Group chat id
last_number = None      # আগের রেজাল্ট নাম্বার চেক করার জন্য

# ==== GET LIVE PREYOD NUMBER ====
def get_market_data():
    try:
        r = requests.get(API_URL, timeout=5)
        data = r.json()
        current = data.get("current", {})
        previous = data.get("previous", {})
        return current.get("issueNumber"), previous.get("issueNumber")
    except Exception as e:
        print("API Error:", e)
        return None, None

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
        await update.message.reply_text(f"👉 Join here: {REF_LINK}")

async def signal_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global signal_running, target_chat_id
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("❌ Only owner can start signals")

    signal_running = True
    target_chat_id = update.effective_chat.id
    await update.message.reply_text("✅ Auto Signal Started in this Group")

    asyncio.create_task(auto_signal(context))

async def signal_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global signal_running
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("❌ Only owner can stop signals")

    signal_running = False
    await update.message.reply_text("🛑 Auto Signal Stopped")

# ==== SEND SIGNAL ====
async def send_signal(context: ContextTypes.DEFAULT_TYPE):
    global target_chat_id, last_number
    if not target_chat_id:
        return

    preyod_number, prev_pre = get_market_data()
    if not preyod_number:
        await context.bot.send_message(chat_id=target_chat_id, text="⚠️ API Error - Preyod Number Missing")
        return

    # Random prediction
    number = random.randint(0, 9)
    bet = "SMALL" if number % 2 == 1 else "BIG"

    # যদি আগের নাম্বার মিলে যায় WIN Message দেবে
    if last_number is not None and last_number == number:
        await context.bot.send_message(
            chat_id=target_chat_id,
            text=f"✅ WIN — Profit +৳100\nNext Ready..."
        )

    # Signal message পাঠানো
    message = (
        f"📊 𝑺𝑯𝑨𝑯𝑬𝑫 𝑨𝑰 𝑷𝑹𝑬𝑫𝑰𝑪𝑻𝑰𝑶𝑵\n\n"
        f"Preyod number - {preyod_number}\n"
        f"BET - {bet}\n"
        f"Number - {number}\n"
        f"Maintain - 7/8 Step\n\n"
        f"🔹 Join - {REF_LINK}\n\n"
        f"Owner - @shahedbintarek"
    )
    await context.bot.send_message(chat_id=target_chat_id, text=message)

    # এই নাম্বারকে last_number হিসাবে save করলাম
    last_number = number

# ==== AUTO SIGNAL LOOP ====
async def auto_signal(context: ContextTypes.DEFAULT_TYPE):
    global signal_running
    while signal_running:
        await send_signal(context)
        await asyncio.sleep(60)  # প্রতি ১ মিনিটে signal

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
