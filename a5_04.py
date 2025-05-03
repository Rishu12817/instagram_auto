from database.gp_psql import insert_instagram_post
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import config

flag = False
# Set up the Service object with the path to the updated chromedriver
service = Service("C:\\Users\\rishu\\OneDrive\\Desktop\\xd\\New folder\\instagram_auto\\chromedriver-win64\\chromedriver.exe")
# Set up Chrome options
options = Options()
options.add_argument('--start-maximized')
# Initialize the WebDriver
driver = webdriver.Chrome(service=service, options=options)

def login(driver, max_attempts=3):
    """Attempt login and reattempt if after login the URL is 'https://www.instagram.com/#'."""
    for attempt in range(1, max_attempts + 1):
        driver.get("https://www.instagram.com/accounts/login/")
        try:
            username_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.NAME, 'username'))
            )
            username_field.clear()
            username_field.send_keys(config.cred["user"])
            password_field = driver.find_element(By.NAME, 'password')
            password_field.clear()
            password_field.send_keys(config.cred["passwd"])
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
        except Exception as e:
            print(f"Attempt {attempt}: Error during login input: {e}")
            continue

        try:
            WebDriverWait(driver, 20).until(
                EC.any_of(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'More')]")),
                    EC.url_to_be("https://www.instagram.com/#")
                )
            )
        except TimeoutException:
            print(f"Attempt {attempt}: Timeout waiting for login result.")
            continue

        current_url = driver.current_url
        if current_url == "https://www.instagram.com/#":
            print(f"Attempt {attempt}: Login URL is {current_url}, retrying login.")
            continue
        else:
            print("Login successful!")
            return True
    return False

try:
    # --------------------- Log in ---------------------
    if not login(driver):
        raise Exception("Failed to log in after multiple attempts.")

    # --------------------- Handle Pop-Up ---------------------
    try:
        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Close' and @role='button']"))
        )
        close_button.click()
    except TimeoutException:
        print("No pop-up appeared, continuing.")

    # --------------------- Navigation to Saved Posts ---------------------
    burger_menu = driver.find_element(By.XPATH, "//span[contains(text(), 'More')]")
    burger_menu.click()
    
    saved_menu = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Saved')]"))
    )
    saved_menu.click()
    
    all_posts_menu = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'All posts')]"))
    )
    all_posts_menu.click()

    # Wait for the posts to be present
    posts_xpath = "//a[contains(@class, '_a6hd') and @role='link']"
    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.XPATH, posts_xpath))
    )
    
    # --------------------- Process Posts in Batches ---------------------
    processed_urls = set()
    
    while True:
        # Find posts already loaded on the page
        posts = driver.find_elements(By.XPATH, posts_xpath)
        new_urls = []
        for post in posts:
            href = post.get_attribute("href")
            if href and "/p/" in href and href not in processed_urls:
                new_urls.append(href)
                processed_urls.add(href)
        
        if new_urls:
            print(f"Processing {len(new_urls)} new posts.")
            for post_url in new_urls:
                # Open each post in a new tab to avoid stale element issues
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                driver.get(post_url)
                
                try:
                    username_element = WebDriverWait(driver, 15).until(
                        EC.visibility_of_element_located((By.XPATH, "//span[contains(@class, 'xt0psk2')]"))
                        # EC.visibility_of_element_located((By.XPATH, "//header//div[contains(@class, '_aaqy')]//span"))
                    )
                    user = username_element.text.split()[0]
                    # print(user)
                except Exception as e:
                    print(f"Username not found for post {post_url}: {e}")
                    user = "Unknown"
                
                try:
                    # Wait for the main container of the post to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'xt0psk2')]")))
                    # Find all potential span elements (captions are sometimes nested)
                    caption_elements = driver.find_elements(By.XPATH, "//span[contains(@class, 'xt0psk2')]")
                    # Extract all text from these elements
                    caption = "\n".join([el.text for el in caption_elements if el.text.strip()])
                    # print(caption)
                except Exception as e:
                    print(f"Caption not found for post {post_url}: {e}")
                    caption = ""
                
                post_active_url = driver.current_url
                insert_instagram_post(user, post_active_url, caption)
                print(f"Processed post: {post_active_url}")
                
                # Close current tab and return to the main saved posts tab
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        else:
            # No new posts found in current view; scroll to load more
            prev_count = len(processed_urls)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # brief pause for new posts to load
            posts_after_scroll = driver.find_elements(By.XPATH, posts_xpath)
            if len(posts_after_scroll) <= prev_count:
                print("No new posts loaded, finishing processing.")
                break

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()
    print("Completed successfully")
