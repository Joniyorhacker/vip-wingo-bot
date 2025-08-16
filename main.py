import time
import requests
from datetime import datetime
import random

# ==============================
# CONFIGURATION
# ==============================
BOT_TOKEN = "8348108389:AAGrurEUGwwmozWUXuA3Aa6zN0SG2lpcW7c"
ADMINS = ["@shahedbintarek"]  # একাধিক এডমিন দিতে পারো
REFER_LINK = "https://dkwin9.com/#/register?invitationCode=16532572738"

# ==============================
# FUNCTIONS
# ==============================
def fetch_chat_ids():
    """
    গ্রুপে বট এড করা হলে স্বয়ংক্রিয়ভাবে সব গ্রুপের Chat ID detect করবে।
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    chat_ids = set()
    try:
        resp = requests.get(url).json()
        for update in resp.get("result", []):
            chat = update.get("message", {}).get("chat", {})
            if chat and chat.get("type") in ["group", "supergroup"]:
                chat_ids.add(chat["id"])
        return list(chat_ids)
    except Exception as e:
        print("Error fetching chat IDs:", e)
        return []

def send_signal(chat_id, message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Error sending message to {chat_id}: {e}")

def get_market_signal():
    """
    লাইভ মার্কেট সিগন্যালের জন্য এখানে API/AI logic বসানো যাবে
    বর্তমানে Random সিগন্যাল ব্যবহার হচ্ছে
    """
    signals = ["BUY BTC", "SELL BTC", "HOLD BTC", "BUY ETH", "SELL ETH", "HOLD ETH"]
    return random.choice(signals)

# ==============================
# MAIN LOOP
# ==============================
def main():
    print("KGF VIP New Update Board চালু হচ্ছে...")
    
    chat_ids = []
    while not chat_ids:
        chat_ids = fetch_chat_ids()
        if not chat_ids:
            print("গ্রুপে বটকে মেসেজ পাঠাও এবং অপেক্ষা করো...")
            time.sleep(5)  # ৫ সেকেন্ড পর আবার চেক

    print(f"Detected Chat IDs: {chat_ids}")

    # ২৪/৭ সিগন্যাল পাঠানো
    while True:
        signal = get_market_signal()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = (
            f"[{timestamp}] Signal: {signal}\n"
            f"Refer: {REFER_LINK}\n"
            f"Admin: {', '.join(ADMINS)}"
        )
        for chat_id in chat_ids:
            send_signal(chat_id, message)
        print(message)
        time.sleep(1)  # প্রতি ১ সেকেন্ডে নতুন সিগন্যাল

if __name__ == "__main__":
    main()
