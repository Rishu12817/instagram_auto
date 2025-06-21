from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from database.gp_psql import fetch_instagram_posts
import time
import os

download_dir = os.path.join(os.path.expanduser("~"), "Desktop", "insta_auto")
if not os.path.exists(download_dir):
    os.makedirs(download_dir)
print("Download directory:", download_dir)

# options = Options()
# options.add_argument('--start-maximized')


# show = True  # Set to True to show browser, False for headless mode
show = False  # Set to True to show browser, False for headless mode

options = Options()
options.add_argument('--start-maximized')
if not show:
    options.add_argument('--headless')  # Enable headless mode
    options.add_argument('--disable-gpu')  # For Windows headless stability
    options.add_argument('--window-size=1920,1080')  # Set window size for headless

# driver = webdriver.Chrome(options=options)

prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=options)

rows = fetch_instagram_posts()
if rows:
    for row in rows:
        print("\n---------------Start-------------------")
        username, photo_url, caption, posted = row
        print(f"User: {username},\n\nURL: {photo_url},\n\nCaption: {caption}, Status: {posted}")

        driver.get("https://snapinsta.to/en")

        # Wait for the input box and paste the URL
        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "s_input"))
        )
        input_box.clear()
        input_box.send_keys(photo_url)

        # Prepare user and post-specific download directory
        post_id = photo_url.rstrip('/').split('/')[-1]
        user_post_dir = os.path.join(download_dir, username, post_id)
        if not os.path.exists(user_post_dir):
            os.makedirs(user_post_dir)
        # Set Chrome's download directory for this post
        driver.execute_cdp_cmd(
            "Page.setDownloadBehavior",
            {
                "behavior": "allow",
                "downloadPath": user_post_dir
            }
        )

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
        max_attempts = 3
        attempt = 0
        success = False
        while attempt < max_attempts and not success:
            try:
                # Always check and close ad modal if present before each attempt
                try:
                    close_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.ID, "closeModalBtn"))
                    )
                    close_btn.click()
                    print(f"Ad modal closed before attempt {attempt+1}")
                    time.sleep(1)
                except Exception:
                    print(f"No ad modal to close before attempt {attempt+1}")

                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.ID, "search-result"))
                )
                try:
                    WebDriverWait(driver, 15).until(
                        EC.invisibility_of_element_located((By.ID, "dlModal"))
                    )
                except Exception:
                    pass  # If it doesn't exist, continue

                time.sleep(1)  # Extra safety: let UI update

                try:
                    download_btn = WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable((
                            By.XPATH,
                            "//a[@title='Download Photo' or @title='Download Video']"
                        ))
                    )
                    download_btn.click()
                    print("Download button clicked successfully.")
                    time.sleep(5)  # Wait for download to start

                    # Check if file is downloaded
                    files = os.listdir(user_post_dir)
                    print("Files in download directory:", files)
                    if not files:
                        print("No files downloaded. Retrying download click one more time...")
                        # Try clicking the download button again
                        try:
                            # Again, close ad modal if present
                            try:
                                close_btn = WebDriverWait(driver, 2).until(
                                    EC.element_to_be_clickable((By.ID, "closeModalBtn"))
                                )
                                close_btn.click()
                                print("Ad modal closed before retry click.")
                                time.sleep(1)
                            except Exception:
                                print("No ad modal to close before retry click.")

                            # Try clicking in the background (top-left corner)
                            try:
                                driver.execute_script("document.elementFromPoint(1,1).click();")
                                print("Clicked in the background (top-left corner).")
                                time.sleep(1)
                            except Exception as e2:
                                print(f"Could not click in background: {e2}")

                            download_btn = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((
                                    By.XPATH,
                                    "//a[@title='Download Photo' or @title='Download Video']"
                                ))
                            )
                            download_btn.click()
                            print("Download button clicked again for retry.")
                            time.sleep(5)
                            files = os.listdir(user_post_dir)
                            print("Files in download directory after retry:", files)
                            if not files:
                                print("Still no files downloaded. Taking screenshot for debugging.")
                                driver.save_screenshot(os.path.join(user_post_dir, "Ignore_debug_no_download.png"))
                            else:
                                print("Download successful after retry:", files)
                                success = True
                        except Exception as e3:
                            print("Retry click failed:", e3)
                            driver.save_screenshot(os.path.join(user_post_dir, "debug_no_download_retry.png"))
                    else:
                        print("Download successful:", files)
                        success = True
                except Exception as e:
                    print(f"Download button not found or not clickable (Attempt {attempt+1}):", e)
                    # If download button not found, try clicking in the background and retry in next loop
                    try:
                        # Again, close ad modal if present
                        try:
                            close_btn = WebDriverWait(driver, 2).until(
                                EC.element_to_be_clickable((By.ID, "closeModalBtn"))
                            )
                            close_btn.click()
                            print("Ad modal closed before background click.")
                            time.sleep(1)
                        except Exception:
                            print("No ad modal to close before background click.")

                        driver.execute_script("document.elementFromPoint(1,1).click();")
                        print(f"Clicked in the background (top-left corner). Will retry... (Attempt {attempt+1})")
                        time.sleep(1)
                    except Exception as e2:
                        print(f"Could not click in background: {e2}")
                    attempt += 1
                    if attempt == max_attempts:
                        print("Retry failed after 3 attempts.")
                        driver.save_screenshot("error_screenshot.png")
            except Exception as e:
                print(f"Unexpected error in attempt {attempt+1}: {e}")
                attempt += 1
                if attempt == max_attempts:
                    print("Retry failed after 3 attempts.")
                    driver.save_screenshot("error_screenshot.png")
        print(f"User: {username},\n\nURL: {photo_url},\n\nCaption: {caption}, Status: {posted}")
        print(f"Downloaded files for {username} at {user_post_dir}: {os.listdir(user_post_dir)}")
        print("---------------End-------------------\n\n")
        # break
else:
            print("No Instagram posts found.")

# input("Press Enter to close the browser...")
# driver.quit()

# exit()

