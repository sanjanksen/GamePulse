import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

# -----------------------------
# CONFIG
# -----------------------------
YOUTUBE_URL = "https://www.youtube.com/watch?v=Hc6D6PJu1K4&list=PLRdw3IjKY2gk-3ap7eNjoxxxIP9OolbO-&t=60s"
GAME_CODE = "8RFTMB"
REQUEST_INTERVAL = 2  # seconds

# Supabase endpoints
FUNCTION_URL = "https://xtyufkrsudoktgxyharf.supabase.co/functions/v1/hello"
FUNCTION_URL2 = "https://xtyufkrsudoktgxyharf.supabase.co/functions/v1/update_current_question"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh0eXVma3JzdWRva3RneHloYXJmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODk0NDExNCwiZXhwIjoyMDc0NTIwMTE0fQ.nfM55AufUJkDernamKuRabkquGi1yGlOatUgLjAAsLo"
}

PAYLOAD = {"gameCode": GAME_CODE}

# -----------------------------
# SETUP SELENIUM
# -----------------------------
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")  # prevents GPU crashes
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-software-rasterizer")
    driver = webdriver.Chrome(options=options)
    return driver


# -----------------------------
# SEND API REQUEST
# -----------------------------
def send_request():
    try:
        response = requests.post(FUNCTION_URL2, headers=HEADERS, json=PAYLOAD)
        print(f"Status code: {response.status_code}")
        try:
            print("Response:", response.json())
        except ValueError:
            print("Non-JSON response:", response.text)
    except Exception as e:
        print("Request failed:", e)

    # Schedule next request
    threading.Timer(REQUEST_INTERVAL, send_request).start()


# -----------------------------
# MAIN
# -----------------------------
def main():
    driver = setup_driver()
    driver.get(YOUTUBE_URL)

    # Wait for play button to be clickable
    wait = WebDriverWait(driver, 20)
    play_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ytp-play-button")))
    play_button.click()

    # Initial API request
    response = requests.post(FUNCTION_URL, headers=HEADERS, json=PAYLOAD)
    print("Initial request:", response.status_code, response.text)
    # Start periodic requests
    send_request()

    


if __name__ == "__main__":
    main()
