import os
import sys
import time
import signal
import shutil
import tempfile
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# -----------------------------
# Config
# -----------------------------
youtube_url = "https://youtu.be/QRJ6JJtHZsQ"
game_code = "794PWQ"
request_interval = 2          # seconds between API calls
keep_alive_interval = 30      # seconds between simulated interactions

function_url = "https://xtyufkrsudoktgxyharf.supabase.co/functions/v1/hello"
update_question_url = "https://xtyufkrsudoktgxyharf.supabase.co/functions/v1/update_current_question"
finished_url = "https://xtyufkrsudoktgxyharf.supabase.co/functions/v1/update_finished"

headers = {
    "Content-Type": "application/json",
    # NOTE: Be careful with embedding long-lived secrets in scripts
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh0eXVma3JzdWRva3RneHloYXJmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODk0NDExNCwiZXhwIjoyMDc0NTIwMTE0fQ.nfM55AufUJkDernamKuRabkquGi1yGlOatUgLjAAsLo"
}

payload = {"gameCode": game_code}
isFinishedPayloadFalse = {"gameCode": game_code, "isFinished": False}
isFinishedPayloadTrue = {"gameCode": game_code, "isFinished": True}


# -----------------------------
# Helper functions
# -----------------------------
def setup_driver():
    """Create a temporary Chrome profile and start a Chrome WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    temp_profile = tempfile.mkdtemp(prefix="selenium_profile_")
    options.add_argument(f"--user-data-dir={temp_profile}")

    # Reduce automation flags
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)

    # Remove navigator.webdriver
    try:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
    except Exception:
        pass

    return driver, temp_profile


def keep_alive(driver):
    """Simulate small interactions to prevent YouTube from pausing."""
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        actions = ActionChains(driver)
        actions.move_to_element_with_offset(body, 10, 10).click().perform()
        print("✔ Simulated user interaction to keep video alive")
    except Exception as e:
        print("❌ Keep-alive failed:", e)


def video_has_ended(driver):
    """Check if the video has ended."""
    try:
        return driver.execute_script("""
            const video = document.querySelector('video');
            return video ? video.ended : false;
        """)
    except Exception as e:
        print("Error checking video state:", e)
        return False


def send_requests_loop(driver):
    """Loop: send API requests and keep video alive."""
    last_keep_alive = time.time()

    try:
        while True:
            # --- API request ---
            try:
                response = requests.post(update_question_url, headers=headers, json=payload, timeout=10)
                print(f"API status: {response.status_code}")
                try:
                    print("Response:", response.json())
                except ValueError:
                    print("Non-JSON:", response.text)
            except Exception as e:
                print("API request failed:", e)

            # --- Check video end ---
            if video_has_ended(driver):
                print("🎬 Video has ended!")
                requests.post(finished_url, headers=headers, json=isFinishedPayloadTrue, timeout=10)
                break

            # --- Keep alive ---
            if time.time() - last_keep_alive > keep_alive_interval:
                keep_alive(driver)
                last_keep_alive = time.time()

            time.sleep(request_interval)

    except KeyboardInterrupt:
        print("Stopping requests loop...")


def handle_sigterm(signum, frame):
    """Graceful exit on termination signals."""
    print("Received termination signal, exiting...")
    sys.exit(0)


# -----------------------------
# Main program
# -----------------------------
def main():
    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigterm)

    driver = None
    temp_profile = None

    try:
        driver, temp_profile = setup_driver()
        print(f"Using temporary profile: {temp_profile}")

        driver.get(youtube_url)

        # Wait for play button and click it
        wait = WebDriverWait(driver, 30)
        try:
            play_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ytp-play-button")))
            play_button.click()
            print("▶ Video started")

            # Enter fullscreen automatically
            try:
                fullscreen_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ytp-fullscreen-button")))
                fullscreen_button.click()
                print("⛶ Fullscreen enabled")
            except Exception as e:
                print("Could not enter fullscreen:", e)

        except Exception as e:
            print("Could not find/play video:", e)

        # Initial API request
        try:
            requests.post(function_url, headers=headers, json=payload, timeout=10)
            response = requests.post(finished_url, headers=headers, json=isFinishedPayloadFalse, timeout=10)
            print("Initial request:", response.status_code, response.text)
        except Exception as e:
            print("Initial API request failed:", e)

        # Start periodic loop
        send_requests_loop(driver)

    except SystemExit:
        pass
    except Exception as e:
        print("Fatal error during run:", e)
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                print("Error quitting driver:", e)

        if temp_profile and os.path.exists(temp_profile):
            try:
                shutil.rmtree(temp_profile, ignore_errors=True)
                print(f"Removed temporary profile: {temp_profile}")
            except Exception as e:
                print("Failed to remove temp profile:", e)


if __name__ == "__main__":
    main()
