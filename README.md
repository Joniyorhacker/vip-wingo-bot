# VIP Wingo 1-minute Signal Telegram Bot

24/7 Telegram bot (GitHub → Replit → UptimeRobot)  
Features:
- Owner: **Shahed | KGS Team**
- Referral gate: users must register via your link and submit their UID
- Owner verify → then user can use signals
- Auto 1-minute signal broadcast (window updates)
- VIP/Premium features (role flags, broadcast, stats)
- Streak-guard: avoids monotonous patterns; **no gambling win guarantee**

## Env (.env on Replit)
BOT_TOKEN=your_botfather_token
OWNER_ID=123456789
REF_LINK=https://dkwin9.com/#/register?invitationCode=16532572738

# Optional (if you want webhook later; not needed for polling)
PORT=8080

## Commands (User)
- /start — registration info + link
- /uid <your_uid> — submit DKWIN UID
- /status — shows verification + premium status
- /signal <period> — get one-off signal using period input
- /subscribe — opt-in to 1-minute auto signals
- /unsubscribe — stop auto signals
- /help — quick help

## Commands (Owner/Admin)
- /verify <tg_id> — mark user verified
- /revoke <tg_id> — remove verification
- /premium <tg_id> <days> — grant premium days
- /free <tg_id> — remove premium
- /broadcast <text> — send to all verified
- /users — show counts
- /setwindow <minutes> — set broadcast interval (default 1)

## Deploy: GitHub → Replit → UptimeRobot
1) Create a GitHub repo with these files.
2) Open Replit → “Create Repl from GitHub” → select repo.
3) Replit Secrets (.env): BOT_TOKEN, OWNER_ID, REF_LINK
4) Press **Run** once. It shows “Bot is live!” page.
5) Copy the Replit web URL (like https://<repl>.repl.co) → add to UptimeRobot as HTTP monitor (5-min interval).
6) Keep Replit tab closed; UptimeRobot keeps it alive 24/7.

> If Replit sleeps, UptimeRobot ping hits `keep_alive.py` Flask server which keeps process warm.

## Disclaimer
This bot generates algorithmic “signals” with configurable logic and streak-guard. It does **not** guarantee real outcomes. Use responsibly.
