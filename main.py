import json
import os
import time
from pathlib import Path
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from keep_alive import keep_alive
from signals import generate_signal

# 🔐 BOT CONFIGURATION
BOT_TOKEN = "8348108389:AAGrurEUGwwmozWUXuA3Aa6zN0SG2lpcW7c"
OWNER_ID = 6091430516
REF_LINK = "https://dkwin9.com/#/register?invitationCode=16532572738"
DATA_PATH = "storage/db.json"
DEFAULT_WINDOW_MINUTES = 1

# 🔧 DB INIT
Path("storage").mkdir(exist_ok=True)
if not Path(DATA_PATH).exists():
    with open(DATA_PATH, "w") as f:
        json.dump({
            "users": {},
            "broadcast": [],
            "window_minutes": DEFAULT_WINDOW_MINUTES
        }, f, indent=2)

def _load():
    with open(DATA_PATH) as f:
        return json.load(f)

def _save(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

def _get_user(data, tg_id):
    tg_id = str(tg_id)
    if tg_id not in data["users"]:
        data["users"][tg_id] = {
            "uid": None, "verified": False, "premium_until": 0,
            "subscribed": False, "history": []
        }
    return data["users"][tg_id]

def _now_ts():
    return int(time.time())

def _has_premium(user):
    return user.get("premium_until", 0) > _now_ts()

def _is_owner(user_id):
    return user_id == OWNER_ID

# 📌 Commands

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = _load()
    _get_user(data, user.id)
    _save(data)
    await update.message.reply_text(
        f"👋 Hi {user.first_name}!\n\n"
        f"🔗 Register here:\n{REF_LINK}\n\n"
        f"Then send: `/uid <your_uid>`\n"
        f"Available commands:\n"
        f"• /signal <period>\n• /subscribe\n• /status\n• /unsubscribe\n\n"
        f"Owner: @shahedbintarek\nTeam: KGS | CLUB HACK 6",
        parse_mode="Markdown"
    )

async def uid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = _load()
    user = _get_user(data, update.effective_user.id)
    if not context.args:
        return await update.message.reply_text("Use: /uid <your_uid>")
    user["uid"] = context.args[0].strip()
    _save(data)
    await update.message.reply_text("✅ UID saved! Wait for owner approval.")

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("⛔ Only owner can use this.")
    if not context.args:
        return await update.message.reply_text("Use: /approve <telegram_user_id>")
    
    tg_id = context.args[0].strip()
    data = _load()
    user = _get_user(data, tg_id)
    user["verified"] = True
    user["premium_until"] = _now_ts() + 30*24*60*60  # 30 days premium
    _save(data)
    await update.message.reply_text(f"✅ Approved user {tg_id}")
    try:
        await context.bot.send_message(
            chat_id=int(tg_id),
            text="🎉 You are now verified! Use /start to continue."
        )
    except:
        pass

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = _load()
    user = _get_user(data, update.effective_user.id)
    premium = "✅" if _has_premium(user) else "❌"
    await update.message.reply_text(
        f"📊 Status:\nVerified: {user['verified']}\nPremium: {premium}\nSubscribed: {user['subscribed']}\nUID: {user['uid']}"
    )

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = _load()
    user = _get_user(data, update.effective_user.id)
    if not user["verified"]:
        return await update.message.reply_text("⛔ You're not verified.")
    if not context.args:
        return await update.message.reply_text("Use: /signal <period>")
    
    period = context.args[0].strip()
    sig = generate_signal(period, user.get("history", []))
    user["history"] = (user.get("history", []) + [sig["pick"]])[-20:]
    _save(data)
    
    await update.message.reply_text(
        f"🎯 Signal for `{sig['period']}`:\n"
        f"Pick: **{sig['pick']}**\nConfidence: `{sig['confidence']}`",
        parse_mode="Markdown"
    )

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = _load()
    user = _get_user(data, update.effective_user.id)
    if not user["verified"]:
        return await update.message.reply_text("⛔ You're not verified.")
    user["subscribed"] = True
    _save(data)
    await update.message.reply_text("🔔 Subscribed to auto-signals.")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = _load()
    user = _get_user(data, update.effective_user.id)
    user["subscribed"] = False
    _save(data)
    await update.message.reply_text("🔕 Unsubscribed from auto-signals.")

# 🔁 Auto Signal Task

async def auto_signal_job(app):
    data = _load()
    for tg_id, user in data["users"].items():
        if user.get("verified") and user.get("subscribed"):
            try:
                period = str(int(time.time()) // 60)
                sig = generate_signal(period, user.get("history", []))
                user["history"] = (user.get("history", []) + [sig["pick"]])[-20:]
                _save(data)
                await app.bot.send_message(
                    chat_id=int(tg_id),
                    text=(f"⏱ Signal `{sig['period']}`:\n"
                          f"Pick: **{sig['pick']}**\nConfidence: `{sig['confidence']}`"),
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(f"Failed to send to {tg_id}: {e}")

def schedule_jobs(app):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: auto_signal_job(app), "interval", minutes=1)
    scheduler.start()

def main():
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("uid", uid))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))

    schedule_jobs(app)
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
