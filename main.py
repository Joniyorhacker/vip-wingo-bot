import subprocess, sys

# --- Auto install requests if not installed ---
try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Bot Token & Config
TOKEN = "8380050511:AAHCU4h9lNDkQJMzU44kxE3Nx-Ujm6JTq2c"
OWNER_ID = 6091430516
REF_LINK = "https://dkwin9.com/#/register?invitationCode=16532572738"
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M.json"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

signal_running = False
last_prediction = None  # শেষবার কি প্রেডিকশন করা হয়েছিল (BIG/SMALL)
last_period = None      # শেষ preyod নম্বর


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    if update.effective_user.id == OWNER_ID:
        await update.message.reply_text("✅ Owner Connected\nUse /signal_on to start signals")
    else:
        await update.message.reply_text(
            f"🤖 𝑺𝑯𝑨𝑯𝑬𝑫 𝑨𝑰 𝑷𝑹𝑬𝑫𝑰𝑪𝑻𝑰𝑶𝑵\n\n"
            f"🔹 Auto Wingo 1 Min Signals\n"
            f"🔹 Owner: @shahedbintarek\n\n"
            f"👉 Join here: {REF_LINK}"
        )


async def signal_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Only Owner can start signals"""
    global signal_running
    if update.effective_user.id == OWNER_ID:
        signal_running = True
        await update.message.reply_text("✅ Auto Signal Started")
        asyncio.create_task(auto_signal(context))
    else:
        await update.message.reply_text(f"👉 Join here: {REF_LINK}")


async def signal_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Only Owner can stop signals"""
    global signal_running
    if update.effective_user.id == OWNER_ID:
        signal_running = False
        await update.message.reply_text("🛑 Auto Signal Stopped")
    else:
        await update.message.reply_text(f"👉 Join here: {REF_LINK}")


def get_market_data():
    """Fetch Real Market Data"""
    try:
        r = requests.get(API_URL, timeout=5)
        data = r.json()

        # ⚠️ Adjust this part depending on real JSON structure
        if "data" in data and "list" in data["data"]:
            latest = data["data"]["list"][0]
            return latest.get("period"), latest.get("number")

        return data.get("period"), data.get("number")

    except Exception as e:
        print("API Error:", e)
        return None, None


async def auto_signal(context: ContextTypes.DEFAULT_TYPE):
    """Send signal every 1 minute"""
    global signal_running, last_prediction, last_period
    while signal_running:
        period, number = get_market_data()
        if period and number is not None:
            # নতুন preyod হলে চেক করবো
            if period != last_period:
                # যদি আগের prediction থাকে, তাহলে win/loss result দেখাবো
                if last_prediction is not None:
                    actual = "SMALL" if number % 2 == 1 else "BIG"
                    if last_prediction == actual:
                        await context.bot.send_message(
                            chat_id=OWNER_ID,
                            text="✅ WIN — Next Ready..."
                        )
                    # যদি loss হয় → কিছুই বলবে না

                # এবার নতুন prediction তৈরি
                bet = "SMALL" if number % 2 == 0 else "BIG"  # simple random style
                last_prediction = bet
                last_period = period

                message = (
                    f"🤖 𝑺𝑯𝑨𝑯𝑬𝑫 𝑨𝑰 𝑷𝑹𝑬𝑫𝑰𝑪𝑻𝑰𝑶𝑵\n\n"
                    f"Wingo - 1 Minute\n"
                    f"Step Maintain - 7/8\n\n"
                    f"Preyod Number - {period}\n"
                    f"Bet - [{bet}]\n"
                    f"Join - {REF_LINK}\n\n"
                    f"Owner - @shahedbintarek"
                )
                await context.bot.send_message(chat_id=OWNER_ID, text=message)

        await asyncio.sleep(10)  # প্রতি 10s এ চেক করবে (1 মিনিটে 6 বার চেক)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal_on", signal_on))
    app.add_handler(CommandHandler("signal_off", signal_off))

    print("✅ SHAHED AI Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
