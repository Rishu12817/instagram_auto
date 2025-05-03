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
loop_time = 2
# Set up the Service object with the path to the updated chromedriver
service = Service("C:\\chromedriver-win64\\chromedriver.exe")  # Using double backslashes

# Set up Chrome options
options = Options()
options.add_argument('--start-maximized')

# Set up the WebDriver with the Service object
driver = webdriver.Chrome(service=service, options=options)

try:
    ############################ log in #####################################
    # Open Instagram login page
    driver.get("https://www.instagram.com/accounts/login/")

    # Wait for the username field to be present
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'username'))
    )

    # Enter username and password
    username_field.send_keys(config.cred["user"])
    
    password_field = driver.find_element(By.NAME, 'password')
    password_field.send_keys(config.cred["passwd"])

    # Click the login button
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()

    # Wait for the URL to change after login (Instagram's feed or profile URL)
    WebDriverWait(driver, 10).until(
        EC.url_contains("instagram.com")
    )
    if flag : print("Login successful!")
    ###################### log in finishes ##############################
    time.sleep(15)

    try:
        # Wait for up to 10 seconds for the close button to appear and be clickable
        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Close' and @role='button']"))
        )
        close_button.click()
        if flag : print("Closed pop-up successfully!")
    except TimeoutException:
        print("Close button did not appear, continuing execution.")

    ####################### Navigate to saved posts #######################
    burgur_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'More')]"))
    )
    burgur_menu.click()
    time.sleep(3)

    saved_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Saved')]"))
    )
    saved_menu.click()
    if flag : print("Successfully navigated to saved posts")
    time.sleep(2)

    all_posts_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'All posts')]"))
    )
    all_posts_menu.click()
    if flag : print("Successfully navigated into saved posts collection")
    time.sleep(2)
    ####################### End of navigation #######################

    # Store the posts list page URL so we can detect navigation changes
    posts_list_url = driver.current_url
    # Define an XPath that uniquely selects each of the clickable post elements.
    posts_xpath = "//a[contains(@class, '_a6hd') and @role='link']"

    # Wait until the posts are loaded
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, posts_xpath))
    )

    # Get the total number of posts
    post_elements = driver.find_elements(By.XPATH, posts_xpath)
    total_posts = len(post_elements)
    print(f"Found {total_posts - 19} posts.")
    
    # Iterate over each post
    for i in range(total_posts):
        posts = driver.find_elements(By.XPATH, posts_xpath)
        post = posts[i]
        href = post.get_attribute("href")
        
        # Skip if the URL doesn't look like a normal post URL
        if "/p/" not in href:
            print(f"Skipping post {i + 1} due to invalid URL: {href}")
            continue

        driver.execute_script("arguments[0].scrollIntoView(true);", post)
        post.click()
        time.sleep(loop_time)
        # time.sleep(50)
############################# proflie name ###############################
        try:
            # Wait for the username to appear
            username_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//header//div[contains(@class, '_aaqy')]//span"))
            )
            user = username_elements.text.split()[0]
        except Exception as e:
            print("Username not found:", e)
############################# proflie name ###############################


############################ caption of the post ###########################
        try:
            # Wait for the caption to appear
            caption_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h1[contains(@class, '_ap3a')]"))
            )
            caption = caption_elements.text
            if flag : print("\nCaption:\n", caption,"\n\n")
        except Exception as e:
            print("Caption not found:", e)
############################ caption of the post ###########################

#################################################################

        time.sleep(loop_time)
        if flag : print("\nClicked on:", post)
        if flag : print("Current URL before wait:", driver.current_url)
        if flag : print(f"Post {i + 1} URL: {driver.current_url}")



        post_profile_name = user
        post_active_url = driver.current_url
        post_caption = caption
        insert_instagram_post(post_profile_name, post_active_url, post_caption)
    

        # Go back to the posts list
        driver.back()
        
        # Wait until we are back on the posts list
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, posts_xpath))
        )
        time.sleep(loop_time)
        if flag : print(f"---post no. {i + 1}----------Process Ended-----------------\n\n")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the browser
    driver.quit()
    print("Completed successfully")