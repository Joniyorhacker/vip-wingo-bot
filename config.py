import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
REF_LINK = os.getenv("REF_LINK", "https://dkwin9.com/#/register?invitationCode=16532572738")

# Job/defaults
DEFAULT_WINDOW_MINUTES = 1  # auto-signal interval
DATA_PATH = "storage/db.json"

# Simple guardrails
MAX_STREAK_SAME_COLOR = 6  # avoid 7 same-type picks in a row
