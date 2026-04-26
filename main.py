from datetime import datetime
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from selenium.webdriver.chrome.options import Options

# ---------- CONFIG ----------
CHECK_INTERVAL = 1800  # 30 mins

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
def notify(message):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Telegram not configured")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram error:", e)

# ---------- YOUR FETCH FUNCTION ----------
def fetch_status():
    options = Options()

    # modern headless
    options.add_argument("--headless=new")

    # stability flags (VERY important)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    wait = WebDriverWait(driver, 10)

    # Open tracking page
    driver.get("https://www.passportindia.gov.in/psp/trackApplicationService")

    time.sleep(3) # Wait for page to load

    dropdown = Select(driver.find_element(By.CSS_SELECTOR, "select.form-select"))

    dropdown.select_by_value("Application_Status")

    file_input = driver.find_element(By.ID, "formBasicEmail")
    file_input.send_keys("CO2076688155426")

    dob_input = driver.find_element(By.CSS_SELECTOR, "input[type='date']")
    dob_input.send_keys("08-05-2008")

    # Submit
    submit_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "checkAppointmentButton")))
    submit_btn.click()

    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "trackApplicationServiceList")))

    rows = driver.find_elements(By.CLASS_NAME, "trackApplicationServiceList")
    row = rows[-1]

    label = row.find_element(By.TAG_NAME, "b").text
    value = row.find_element(By.TAG_NAME, "span").text
    status = f"{label}: {value}"

    status = f"""
📄 Passport Update

{status}

⏱ {time.ctime()}
"""

    driver.quit()

    return status

# ---------- MAIN CHECK ----------
def check_for_update():
    log("Checking status...")
    
    new_status = fetch_status()
    old_status = load_last_status()

    if new_status != old_status:
        log(f"Status changed: {new_status}")
        save_status(new_status)

        notify("Passport Update" + new_status)
        print("🔔 Status changed:", new_status)
    else:
        log("No change")
        print("No change")

# ---------- START ----------
def main():
    notify("Tracker Started" + "Passport tracker is running")
    log("Tracker started")

    while True:
        try:
            check_for_update()
        except Exception as e:
            log(f"Error: {e}")
            print("Error:", e)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()