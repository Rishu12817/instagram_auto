from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from database.gp_psql import fetch_instagram_posts
import time

show = False  # Set to True to show browser, False for headless mode

options = Options()
options.add_argument('--start-maximized')
if not show:
    options.add_argument('--headless')  # Enable headless mode
    options.add_argument('--disable-gpu')  # For Windows headless stability
    options.add_argument('--window-size=1920,1080')  # Set window size for headless

driver = webdriver.Chrome(options=options)

rows = fetch_instagram_posts()
if rows:
    for row in rows:
        print("----------------------------------")
        username, photo_url, caption, posted = row
        # print(f"User: {username},\n\nURL: {photo_url},\n\nCaption: {caption}, Status: {posted}")
        print("----------------------------------")

        driver.get("https://snapinsta.to/en")

        # Wait for the input box and paste the URL
        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "s_input"))
        )
        input_box.clear()
        input_box.send_keys(photo_url)

        # Click the Download button
        download_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-default') and contains(., 'Download')]"))
        )
        download_btn.click()

        # Wait for the modal and close it (ad may not always appear)
        try:
            close_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "closeModalBtn"))
            )
            close_btn.click()
        except Exception:
            print("No ad modal appeared, continuing...")

        # Wait for the "Download Photo" or "Download Video" button and click it
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "search-result"))
            )
            download_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//a[@title='Download Photo' or @title='Download Video']"
                ))
            )
            download_btn.click()
            time.sleep(5)  # Wait for download to start
        except Exception as e:
            print("Download button not found or not clickable:", e)
            driver.save_screenshot("error_screenshot.png")
else:
            print("No Instagram posts found.")

# input("Press Enter to close the browser...")
# driver.quit()

# exit()

