import json, os, urllib.request
from pathlib import Path

PRODUCT_ID = "548194754"
WANTED_SIZE = "41"
PRODUCT_URL = "https://www.zara.com/cz/en/topstitched-heel-mules-p12306710.html?v1=548194754"
API_URL = "https://www.zara.com/cz/en/products-details?productIds=" + PRODUCT_ID + "&ajax=true"
NTFY_TOPIC = os.environ["NTFY_TOPIC"]
STATE_FILE = Path("state.json")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"


def notify(title, message, priority="high", tags="tada"):
    req = urllib.request.Request(
        "https://ntfy.sh/" + NTFY_TOPIC,
        data=message.encode("utf-8"),
        headers={"Title": title, "Priority": priority, "Tags": tags, "Click": PRODUCT_URL},
    )
    urllib.request.urlopen(req, timeout=20)
    print("Notification sent: " + title)


req = urllib.request.Request(API_URL, headers={"User-Agent": UA, "Accept": "application/json", "Accept-Language": "en-GB,en;q=0.9"})
data = json.load(urllib.request.urlopen(req, timeout=20))
color = data[0]["detail"]["colors"][0]
price = color["price"] / 100  # v Kc
availability = next((s.get("availability", "unknown") for s in color.get("sizes", []) if s.get("name") == WANTED_SIZE), "size_not_listed")
print("Size " + WANTED_SIZE + ": " + availability + " | price: " + str(price) + " Kc")

state = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}
prev_price = state.get("lowest_price")
prev_avail = state.get("availability")

# 1) restock notifikacia
if availability in ("in_stock", "low_on_stock") and prev_avail not in ("in_stock", "low_on_stock"):
    notify("Zara restock", "Velkost " + WANTED_SIZE + " je SKLADOM (" + availability + ")!\n" + PRODUCT_URL, priority="urgent")

# 2) cenova notifikacia
if prev_price is None:
    notify("Zara watch aktivny", "Sledujem cenu aj velkost " + WANTED_SIZE + ". Aktualna cena: " + str(price) + " Kc", priority="default", tags="white_check_mark")
elif price < prev_price:
    notify("Zara CENA KLESLA", "Nova cena: " + str(price) + " Kc (predtym " + str(prev_price) + " Kc)\n" + PRODUCT_URL, priority="urgent", tags="chart_with_downwards_trend")

state["lowest_price"] = price if prev_price is None else min(prev_price, price)
state["availability"] = availability
state["last_price"] = price
STATE_FILE.write_text(json.dumps(state))
