"""
Scrapes the public GitHub contributions calendar (no auth/token needed) and
writes data/contributions.json with raw days + derived stats used by
make_info_card.py and render_heatmap_svg.py.
"""
import json
import re
import sys
from datetime import datetime, date
import requests
from bs4 import BeautifulSoup

USERNAME = "01-de"  # <-- change if needed

def fetch_contribution_days(username):
    url = f"https://github.com/users/{username}/contributions"
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    # GitHub renders each day as a <td> with data-date and data-level (newer markup)
    # or <rect> with data-date + data-count (older markup) — handle both.
    cells = soup.select("td.ContributionCalendar-day")
    if cells:
        for td in cells:
            d = td.get("data-date")
            level = td.get("data-level")
            if d is None:
                continue
            tooltip_id = td.get("id")
            count = 0
            if tooltip_id:
                tip = soup.find(attrs={"for": tooltip_id}) or soup.find(id=f"tooltip-{tooltip_id}")
            # fallback: parse count from level if tooltip not found (level is 0-4 intensity)
            days.append({"date": d, "level": int(level) if level else 0})
    else:
        rects = soup.select("rect[data-date]")
        for r in rects:
            d = r.get("data-date")
            count = r.get("data-count")
            days.append({"date": d, "count": int(count) if count else 0})

    return days

def compute_stats(days):
    # normalize: ensure each day has a numeric weight to sum/streak on
    def weight(d):
        return d.get("count", d.get("level", 0))

    days_sorted = sorted(days, key=lambda d: d["date"])
    total = sum(weight(d) for d in days_sorted)

    # current streak: count consecutive days with weight > 0, walking backward from today
    today = date.today().isoformat()
    by_date = {d["date"]: weight(d) for d in days_sorted}
    streak = 0
    cursor = date.today()
    while True:
        key = cursor.isoformat()
        if by_date.get(key, 0) > 0:
            streak += 1
            cursor = cursor.fromordinal(cursor.toordinal() - 1)
        else:
            # allow today to be zero (day not over yet) without breaking streak
            if key == today and streak == 0:
                cursor = cursor.fromordinal(cursor.toordinal() - 1)
                continue
            break

    longest = 0
    run = 0
    for d in days_sorted:
        if weight(d) > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0

    return {
        "total_contributions": total,
        "current_streak": streak,
        "longest_streak": longest,
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }

if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else USERNAME
    days = fetch_contribution_days(username)
    if not days:
        print("WARNING: no contribution cells parsed — GitHub markup may have changed.", file=sys.stderr)
    stats = compute_stats(days)
    out = {"username": username, "days": days, "stats": stats}
    import os
    os.makedirs("data", exist_ok=True)
    with open("data/contributions.json", "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(stats, indent=2))
