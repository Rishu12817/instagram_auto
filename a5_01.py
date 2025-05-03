from database.gp_psql import insert_instagram_post
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
import config

def load_all_posts(driver, posts_xpath, scroll_pause=2):
    """
    Scrolls down the page until no new posts are loaded.
    """
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def is_valid_post_url(url):
    """
    Returns True if the URL looks like an individual Instagram post.
    This function filters out URLs that contain paths like 'saved', 'legal', 'explore', etc.
    """
    if not url:
        return False
    if "/p/" not in url:
        return False
    invalid_keywords = ["saved", "legal", "explore", "direct", "threads", "accounts", "web/lite"]
    for word in invalid_keywords:
        if word in url:
            return False
    return True

flag = False  # Set to True for additional debug prints
loop_time = 2

# Set up the Service object with the path to your updated chromedriver
service = Service("C:\\chromedriver-win64\\chromedriver.exe")
options = Options()
options.add_argument('--start-maximized')
driver = webdriver.Chrome(service=service, options=options)

try:
    # ------------------- Log in -------------------
    driver.get("https://www.instagram.com/accounts/login/")
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'username'))
    )
    username_field.send_keys(config.cred["user"])
    password_field = driver.find_element(By.NAME, 'password')
    password_field.send_keys(config.cred["passwd"])
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()
    
    # Wait for login to complete
    WebDriverWait(driver, 10).until(EC.url_contains("instagram.com"))
    if flag:
        print("Login successful!")
    time.sleep(15)  # Wait for potential pop-ups
    
    try:
        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Close' and @role='button']"))
        )
        close_button.click()
        if flag:
            print("Closed pop-up successfully!")
    except TimeoutException:
        print("Close button did not appear, continuing execution.")
    
    # ------------------- Navigate to Saved Posts -------------------
    burgur_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'More')]"))
    )
    burgur_menu.click()
    time.sleep(3)
    
    saved_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Saved')]"))
    )
    saved_menu.click()
    if flag:
        print("Successfully navigated to saved posts")
    time.sleep(2)
    
    all_posts_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'All posts')]"))
    )
    all_posts_menu.click()
    if flag:
        print("Successfully navigated into saved posts collection")
    time.sleep(2)
    
    # ------------------- Scroll to Load All Posts -------------------
    posts_xpath = "//a[contains(@class, '_a6hd') and @role='link']"
    load_all_posts(driver, posts_xpath, scroll_pause=2)
    
    # ------------------- Collect Valid Post URLs -------------------
    post_elements = driver.find_elements(By.XPATH, posts_xpath)
    post_urls = []
    for post in post_elements:
        href = post.get_attribute("href")
        if is_valid_post_url(href):
            post_urls.append(href)
        else:
            print(f"Skipping invalid URL: {href}")
    total_posts = len(post_urls)
    print(f"Found {total_posts} valid posts.")
    
    # ------------------- Process Each Post -------------------
    for idx, url in enumerate(post_urls, start=1):
        try:
            driver.get(url)
            time.sleep(loop_time)
            
            # ------------------- Extract Profile Name -------------------
            try:
                username_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//header//div[contains(@class, '_aaqy')]//span")
                    )
                )
                user = username_element.text.split()[0]
            except Exception as e:
                print(f"Username not found for post {idx}: {e}")
                user = "Unknown"
            
            # ------------------- Extract Caption -------------------
            try:
                caption_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//h1[contains(@class, '_ap3a')]")
                    )
                )
                caption = caption_element.text
                if flag:
                    print(f"\nCaption for post {idx}:\n{caption}\n")
            except Exception as e:
                print(f"Caption not found for post {idx}: {e}")
                caption = ""
            
            post_profile_name = user
            post_active_url = driver.current_url
            post_caption = caption
            
            # Insert data into the database
            insert_instagram_post(post_profile_name, post_active_url, post_caption)
            print(f"Processed post {idx}: {post_active_url}")
            time.sleep(loop_time)
            
        except Exception as e:
            print(f"Error processing post {idx} at {url}: {e}")
            continue

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()
    print("Completed successfully")
