import json
import os
import time
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List

from telegram import Update, ForceReply
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes,
)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from keep_alive import keep_alive
from config import BOT_TOKEN, OWNER_ID, REF_LINK, DEFAULT_WINDOW_MINUTES, DATA_PATH
from signals import generate_signal

# ---------- storage ----------
Path("storage").mkdir(exist_ok=True)
if not Path(DATA_PATH).exists():
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "users": {},      # tg_id -> {"uid": str|None, "verified": bool, "premium_until": ts|0, "subscribed": bool, "history": [str]}
            "broadcast": [],  # last messages ids if needed
            "window_minutes": DEFAULT_WINDOW_MINUTES
        }, f, ensure_ascii=False, indent=2)

def _load() -> Dict[str, Any]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(data: Dict[str, Any]):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _get_user(data, tg_id: int):
    tg_id = str(tg_id)
    if tg_id not in data["users"]:
        data["users"][tg_id] = {
            "uid": None, "verified": False, "premium_until": 0,
            "subscribed": False, "history": []
        }
    return data["users"][tg_id]

def _is_owner(user_id: int) -> bool:
    return OWNER_ID and user_id == OWNER_ID

def _now_ts() -> int:
    return int(time.time())

def _has_premium(u: Dict[str, Any]) -> bool:
    return u.get("premium_until", 0) > _now_ts()

# ---------- bot handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    data = _load()
    _get_user(data, u.id)
    _save(data)
    text = (
        f"👋 Hi {u.first_name}!\n\n"
        f"🔗 **Register First** using this link:\n{REF_LINK}\n\n"
        f"Then send your UID using:\n`/uid <your_uid>`\n\n"
        f"After owner verification, you can:\n"
        f"• `/signal <period>` — one-off signal\n"
        f"• `/subscribe` — get auto 1-minute signals\n"
        f"• `/status` — check status\n"
        f"• `/help` — all commands\n\n"
        f"Owner: @shahedbintarek | KGS Team"
    )
    await update.message.reply_text(text, disable_web_page_preview=True)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = _is_owner(update.effective_user.id)
    user_part = (
        "🧩 User Commands:\n"
        "• /start — registration intro\n"
        "• /uid <your_uid> — submit your DKWIN UID\n"
        "• /status — your status\n"
        "• /signal <period> — get a signal\n"
        "• /subscribe — auto 1-minute signals\n"
        "• /unsubscribe — stop auto signals\n"
    )
    admin_part = (
        "\n🛠 Admin Commands:\n"
        "• /verify <tg_id>\n"
        "• /revoke <tg_id>\n"
        "• /premium <tg_id> <days>\n"
        "• /free <tg_id>\n"
        "• /broadcast <text>\n"
        "• /users — counts\n"
        "• /setwindow <minutes> — default 1\n"
    )
    await update.message.reply_text(user_part + (admin_part if is_admin else ""))

async def uid_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = _load()
    u = _get_user(data, update.effective_user.id)
    if not context.args:
        return await update.message.reply_text("Send like: `/uid 12345678`", parse_mode="Markdown")
    u["uid"] = context.args[0].strip()
    _save(data)
    await update.message.reply_text("✅ UID received! Wait for owner verification.")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = _load()
    u = _get_user(data, update.effective_user.id)
    premium = "Yes" if _has_premium(u) else "No"
    await update.message.reply_text(
        f"🔎 Status:\nVerified: {u['verified']}\nPremium: {premium}\nSubscribed: {u['subscribed']}\nUID: {u['uid']}"
    )

async def subscribe_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = _load()
    u = _get_user(data, update.effective_user.id)
    if not u["verified"]:
        return await update.message.reply_text("You must be verified by owner first.")
    u["subscribed"] = True
    _save(data)
    await update.message.reply_text("🔔 Subscribed. You will receive 1-minute signals.")

async def unsubscribe_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = _load()
    u = _get_user(data, update.effective_user.id)
    u["subscribed"] = False
    _save(data)
    await update.message.reply_text("🔕 Unsubscribed from auto signals.")

async def signal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = _load()
    user = _get_user(data, update.effective_user.id)
    if not user["verified"]:
        return await update.message.reply_text("You are not verified yet. Ask owner to verify.")
    if not context.args:
        return await update.message.reply_text("Use: `/signal <period>`", parse_mode="Markdown")
    period = context.args[0].strip()
    sig = generate_signal(period, user.get("history", []))
    # update history
    user["history"] = (user.get("history", []) + [sig["pick"]])[-20:]
    _save(data)
    await update.message.reply_text(
        f"🎯 Signal (window {sig['window']}):\n"
        f"Period: `{sig['period']}`\nPick: **{sig['pick']}**\nConfidence: `{sig['confidence']}`",
        parse_mode="Markdown"
    )

# ----- Admin -----
async def verify_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_owner(update.effective_user.id):
        return
    if not context.args:
        return await update.message.reply_text("Use: /verify <tg_id>")
    tg_id = context.args[0].strip()
    data = _load()
    u = _get_user(data, tg_id)
    u["verified"] = True
    _save(data)
    await update.message.reply_text(f"✅ Verified user {tg_id}")

async def revoke_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_owner(update.effective_user.id):
        return
    if not context.args:
        return await update.message.reply_text("Use: /revoke <tg_id>")
    tg_id = context.args[0].strip()
    data = _load()
    u = _get_user(data, tg_id)
    u["verified"] = False
    u["subscribed"] = False
    _save(data)
    await update.message.reply_text(f"♻️ Revoked user {tg_id}")

async def premium_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_owner(update.effective_user.id):
        return
    if len(context.args) < 2:
        return await update.message.reply_text("Use: /premium <tg_id> <days>")
    tg_id = context.args[0].strip()
    days = int(context.args[1])
    data = _load()
    u = _get_user(data, tg_id)
    u["premium_until"] = int(time.time() + days * 86400)
    _save(data)
    await update.message.reply_text(f"🌟 Premium granted for {tg_id} ({days} days).")

async def free_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_owner(update.effective_user.id):
        return
    if not context.args:
        return await update.message.reply_text("Use: /free <tg_id>")
    tg_id = context.args[0].strip()
    data = _load()
    u = _get_user(data, tg_id)
    u["premium_until"] = 0
    _save(data)
    await update.message.reply_text(f"🆓 Premium removed for {tg_id}.")

async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_owner(update.effective_user.id):
        return
    if not context.args:
        return await update.message.reply_text("Use: /broadcast <text>")
    text = " ".join(context.args)
    data = _load()
    users = list(data["users"].items())
    ok = 0
    for tg_id, u in users:
        if u.get("verified"):
            try:
                await context.bot.send_message(chat_id=int(tg_id), text=f"📣 Broadcast:\n{text}")
                ok += 1
            except Exception:
                pass
    await update.message.reply_text(f"Broadcast sent to {ok} verified users.")

async def users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_owner(update.effective_user.id):
        return
    d = _load()
    total = len(d["users"])
    verified = sum(1 for u in d["users"].values() if u.get("verified"))
    subs = sum(1 for u in d["users"].values() if u.get("subscribed"))
    await update.message.reply_text(f"👥 Users: total {total}, verified {verified}, subscribed {subs}")

async def setwindow_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_owner(update.effective_user.id):
        return
    if not context.args:
        return await update.message.reply_text("Use: /setwindow <minutes>")
    m = max(1, int(context.args[0]))
    d = _load()
    d["window_minutes"] = m
    _save(d)
    await update.message.reply_text(f"⏱ Window set to {m} minutes. (Job will pick it next tick)")

# ----- Auto job -----
async def run_auto_signals(app):
    d = _load()
    window = d.get("window_minutes", DEFAULT_WINDOW_MINUTES)
    # iterate all verified & subscribed
    for tg_id, u in list(d["users"].items()):
        if u.get("verified") and u.get("subscribed"):
            try:
                period = str(int(time.time()) // 60)  # simple rolling period
                sig = generate_signal(period, u.get("history", []))
                u["history"] = (u.get("history", []) + [sig["pick"]])[-20:]
                _save(d)
                await app.bot.send_message(
                    chat_id=int(tg_id),
                    text=(f"⏱ [Auto {sig['window']}] Period: `{sig['period']}`\n"
                          f"Pick: **{sig['pick']}** | Confidence: `{sig['confidence']}`"),
                    parse_mode="Markdown"
                )
            except Exception:
                pass

def schedule_jobs(application):
    scheduler = AsyncIOScheduler()
    async def job():
        await run_auto_signals(application)
    # run every minute
    scheduler.add_job(job, "interval", minutes=1, next_run_time=datetime.utcnow())
    scheduler.start()

# ---------- bootstrap ----------
def main():
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN missing in env.")
    keep_alive()

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("uid", uid_cmd))
    application.add_handler(CommandHandler("status", status_cmd))
    application.add_handler(CommandHandler("subscribe", subscribe_cmd))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe_cmd))
    application.add_handler(CommandHandler("signal", signal_cmd))

    # admin
    application.add_handler(CommandHandler("verify", verify_cmd))
    application.add_handler(CommandHandler("revoke", revoke_cmd))
    application.add_handler(CommandHandler("premium", premium_cmd))
    application.add_handler(CommandHandler("free", free_cmd))
    application.add_handler(CommandHandler("broadcast", broadcast_cmd))
    application.add_handler(CommandHandler("users", users_cmd))
    application.add_handler(CommandHandler("setwindow", setwindow_cmd))

    schedule_jobs(application)
    application.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
