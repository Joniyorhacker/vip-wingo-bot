import time
import math
import random
from typing import Dict, Tuple, Optional, List
from config import MAX_STREAK_SAME_COLOR

# Define your palette / playside universe (customize as you wish)
COLORS = ["GREEN", "RED", "VIOLET"]

def _seed_from(period: str, now_ts: Optional[int] = None) -> int:
    """
    Deterministic-ish seed from period string + current minute bucket.
    Makes output change every minute window but stable within that minute.
    """
    period = str(period).strip()
    bucket = int((now_ts or int(time.time())) // 60)  # per-minute window
    return hash(f"{period}:{bucket}") & 0xFFFFFFFF

def _pick_with_streak_guard(history: List[str]) -> str:
    """
    Avoids outputting same color > MAX_STREAK_SAME_COLOR consecutively.
    If history has a long tail of same color, pick something else.
    """
    if not history:
        return random.choice(COLORS)
    last = history[-1]
    tail = 0
    for c in reversed(history):
        if c == last:
            tail += 1
        else:
            break
    if tail >= MAX_STREAK_SAME_COLOR:
        # force switch
        options = [c for c in COLORS if c != last]
        return random.choice(options)
    return random.choice(COLORS)

def generate_signal(period: str, history: List[str]) -> Dict:
    """
    Core signal generator. Streak-guard only controls bot's own output pattern,
    it does NOT guarantee external game outcomes.
    """
    seed = _seed_from(period)
    rnd = random.Random(seed)
    random.choice  # just to keep linter calm
    # pick candidate then run streak guard on top of it
    candidate = rnd.choice(COLORS)
    # blend with guard by sometimes enforcing guard outcome
    if rnd.random() < 0.55:
        # 55% of the time, obey guard
        pick = _pick_with_streak_guard(history)
    else:
        pick = candidate

    # Confidence is synthetic; you can tune per color
    confidence = round(0.60 + 0.35 * rnd.random(), 2)  # 0.60 .. 0.95

    return {
        "period": str(period),
        "pick": pick,
        "confidence": confidence,
        "window": "1m",
  }
