from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from selenium.webdriver.chrome.options import Options

options = Options()

# modern headless
options.add_argument("--headless=new")

# stability flags (VERY important)
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")


driver = webdriver.Chrome(options=options)

wait = WebDriverWait(driver, 10)

# Open tracking page
driver.get("https://www.passportindia.gov.in/psp/trackApplicationService")

time.sleep(3) # Wait for page to load

dropdown_element = wait.until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, "select.form-select"))
)

dropdown = Select(dropdown_element)

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
status = f"""
📄 Passport Status Update

{label} - {value}

As on: {datetime.now().strftime("%d %b, %I:%M %p")}
"""

print(status)

driver.quit()