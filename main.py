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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command response"""
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
    """Fetch Real Market Period & Number"""
    try:
        r = requests.get(API_URL, timeout=5)
        data = r.json()
        return data.get("period"), data.get("number")
    except Exception as e:
        print("API Error:", e)
        return None, None


async def auto_signal(context: ContextTypes.DEFAULT_TYPE):
    """Send auto signals to owner only"""
    global signal_running
    while signal_running:
        period, number = get_market_data()
        if period and number is not None:
            bet = "SMALL" if number % 2 == 1 else "BIG"

            message = (
                f"𝑺𝑯𝑨𝑯𝑬𝑫 𝑨𝑰 𝑷𝑹𝑬𝑫𝑰𝑪𝑻𝑰𝑶𝑵\n\n"
                f"Wingo - 1 minutes\n"
                f"Step maintain - 7/8\n"
                f"Preyod number - {period}\n"
                f"Bet - [ {bet} ]\n"
                f"Number - [ {number} ]\n"
                f"Join - {REF_LINK}"
            )

            # Send only to Owner inbox
            try:
                await context.bot.send_message(chat_id=OWNER_ID, text=message)
            except Exception as e:
                print("Send Error:", e)

        await asyncio.sleep(60)  # প্রতি 1 মিনিটে


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal_on", signal_on))
    app.add_handler(CommandHandler("signal_off", signal_off))

    print("✅ SHAHED AI Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
