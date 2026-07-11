import json, os, urllib.request
PRODUCT_ID = "548194754"
WANTED_SIZE = "41"
PRODUCT_URL = "https://www.zara.com/cz/en/topstitched-heel-mules-p12306710.html?v1=548194754"
API_URL = "https://www.zara.com/cz/en/products-details?productIds=" + PRODUCT_ID + "&ajax=true"
NTFY_TOPIC = os.environ["NTFY_TOPIC"]
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
req = urllib.request.Request(API_URL, headers={"User-Agent": UA, "Accept": "application/json", "Accept-Language": "en-GB,en;q=0.9"})
data = json.load(urllib.request.urlopen(req, timeout=20))
availability = next((s.get("availability", "unknown") for c in data[0]["detail"]["colors"] for s in c.get("sizes", []) if s.get("name") == WANTED_SIZE), "size_not_listed")
print("Size " + WANTED_SIZE + ": " + availability)
msg = ("Velkost " + WANTED_SIZE + " je SKLADOM (" + availability + ")!\n" + PRODUCT_URL).encode("utf-8")
ntfy = urllib.request.Request("https://ntfy.sh/" + NTFY_TOPIC, data=msg, headers={"Title": "Zara restock", "Priority": "high", "Tags": "tada"})
if availability in ("in_stock", "low_on_stock"): urllib.request.urlopen(ntfy, timeout=20); print("Notification sent.")
