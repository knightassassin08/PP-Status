from datetime import datetime
import requests
from playwright.sync_api import sync_playwright
import time
import os

# ---------- CONFIG ----------
CHECK_INTERVAL = 1800  # 30 mins
TELEGRAM_CHAT_ID = "8659477480"
TELEGRAM_TOKEN = "8737828968:AAEv0gt8uUWe0Yb0EP-WiBL_TC_h5pcGeSA"

# ---------- STORAGE ----------
def load_last_status():
    try:
        with open("status.txt", "r") as f:
            return f.read().strip()
    except:
        return ""

def save_status(status):
    with open("status.txt", "w") as f:
        f.write(status)

# ---------- LOG ----------
def log(message):
    with open("log.txt", "a") as f:
        f.write(f"{datetime.now()} - {message}\n")

# ---------- NOTIFICATION ----------
def notify(message, silent=False):
    #token = os.getenv("TELEGRAM_TOKEN")
    #chat_id = os.getenv("TELEGRAM_CHAT_ID")

    token = TELEGRAM_TOKEN
    chat_id = TELEGRAM_CHAT_ID

    if not token or not chat_id:
        print("Telegram not configured")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": message,
        "disable_notification": silent  # 🔥 THIS makes it silent
    }

    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram error:", e)

# ---------- YOUR FETCH FUNCTION ----------
def fetch_status():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Open page
        page.goto("https://www.passportindia.gov.in/psp/trackApplicationService")

        # Select dropdown
        page.select_option("select.form-select", "Application_Status")

        # Fill inputs
        page.fill("#formBasicEmail", "CO2076688155426")

        # IMPORTANT: Playwright needs YYYY-MM-DD
        page.fill("input[type='date']", "2008-05-08")

        # Click submit
        page.click(".checkAppointmentButton")

        # Wait for results
        page.wait_for_selector(".trackApplicationServiceList")

        # Get all rows
        rows = page.locator(".trackApplicationServiceList")

        count = rows.count()
        last_row = rows.nth(count - 1)

        label = last_row.locator("b").inner_text()
        value = last_row.locator("span").nth(1).inner_text()

        status = f"{label}: {value}"

        status = f"""
📄 Passport Update

{status}

⏱ {time.ctime()}
"""

        browser.close()
        return status

# ---------- MAIN CHECK ----------
def check_for_update():
    log("Checking status...")
    
    new_status = fetch_status()
    old_status = load_last_status()

    if new_status != old_status:
        log(f"Status changed: {new_status}")
        save_status(new_status)

        notify(new_status)
        print(new_status)
    else:
        log("No change")
        print("No change")

# ---------- START ----------
def main():
    notify("Passport tracker is running")
    log("Tracker started")

    heartbeat_counter = 0

    while True:
        if heartbeat_counter % 6 == 0:  # every 3 hours (30min * 6)
            notify(f"🟢 Tracker alive ({time.ctime()})", silent=True)

            heartbeat_counter += 1
        
        check_for_update()

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()