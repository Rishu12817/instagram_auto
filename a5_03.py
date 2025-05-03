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
service = Service("C:\\chromedriver-win64\\chromedriver.exe")

# Set up Chrome options
options = Options()
options.add_argument('--start-maximized')

# Initialize the WebDriver
driver = webdriver.Chrome(service=service, options=options)

def login(driver, max_attempts=3):
    """Attempt to log in and reattempt if the URL becomes 'https://www.instagram.com/#'."""
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

        # Wait for either a clickable burger menu (successful login) or the problematic URL.
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

        # Check URL after login
        current_url = driver.current_url
        if current_url == "https://www.instagram.com/#":
            print(f"Attempt {attempt}: Login URL is {current_url}, retrying login.")
            continue
        else:
            print("Login successful!")
            return True
    return False

def scroll_and_collect_post_urls(driver, posts_xpath, scroll_pause=1, max_attempts=10):
    """
    Scrolls through the posts page until no new posts are loaded, then returns a list of valid post URLs.
    """
    collected_urls = set()
    last_count = 0
    attempts = 0

    while attempts < max_attempts:
        posts = driver.find_elements(By.XPATH, posts_xpath)
        for post in posts:
            href = post.get_attribute("href")
            if href and "/p/" in href:
                collected_urls.add(href)
        if len(collected_urls) > last_count:
            last_count = len(collected_urls)
            attempts = 0  # Reset attempts if new posts loaded
        else:
            attempts += 1
        # Scroll to load more posts
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)
    return list(collected_urls)

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
        if flag:
            print("Closed pop-up successfully!")
    except TimeoutException:
        if flag:
            print("No pop-up appeared, continuing.")

    # --------------------- Navigation to Saved Posts ---------------------
    burger_menu = driver.find_element(By.XPATH, "//span[contains(text(), 'More')]")
    burger_menu.click()
    
    saved_menu = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Saved')]"))
    )
    saved_menu.click()
    if flag:
        print("Navigated to Saved Posts")
    
    all_posts_menu = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'All posts')]"))
    )
    all_posts_menu.click()
    if flag:
        print("Entered All Posts collection")
    
    # --------------------- Scroll & Collect Post URLs ---------------------
    posts_xpath = "//a[contains(@class, '_a6hd') and @role='link']"
    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.XPATH, posts_xpath))
    )
    post_urls = scroll_and_collect_post_urls(driver, posts_xpath)
    total_posts = len(post_urls)
    print(f"Collected {total_posts} post URLs.")
    
    # --------------------- Process Each Post ---------------------
    for i, post_url in enumerate(post_urls, start=1):
        # Open each post in a new tab for isolation
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        
        driver.get(post_url)
        
        try:
            username_element = WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located((By.XPATH, "//header//div[contains(@class, '_aaqy')]//span"))
            )
            user = username_element.text.split()[0]
        except Exception as e:
            print(f"Username not found for post {i}: {e}")
            user = "Unknown"
        
        try:
            caption_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//h1[contains(@class, '_ap3a')]"))
            )
            caption = caption_element.text
        except Exception as e:
            print(f"Caption not found for post {i}: {e}")
            caption = ""
        
        post_active_url = driver.current_url
        insert_instagram_post(user, post_active_url, caption)
        print(f"Processed post {i}: {post_active_url}")
        
        # Close the current tab and switch back to the main tab
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.XPATH, posts_xpath)))
    
except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()
    print("Completed successfully")
