from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import config

# Set up the Service object with the path to the updated chromedriver
# service = Service(r"C:\chromedriver-win64\chromedriver.exe")  # Using a raw string
# or
service = Service("C:\\chromedriver-win64\\chromedriver.exe")
# Set up Chrome options
options = Options()
options.add_argument('--start-maximized')

# Set up the WebDriver with the Service object
driver = webdriver.Chrome(service=service, options=options)

############################ log in #####################################
# Open Instagram login page
driver.get("https://www.instagram.com/accounts/login/")

# Wait for the username field to be present
try:
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
    print("Login successful!")
###################### log in finishes ##############################
    time.sleep(10)
#######################
    burgur_menu = driver.find_element(By.XPATH, "//span[contains(text(), 'More')]")
    burgur_menu.click()
###########################
    time.sleep(3)
#######################
    saved_menu = driver.find_element(By.XPATH, "//span[contains(text(), 'Saved')]")
    saved_menu.click()
    print("Successfully navigated to saved posts")
###########################
    time.sleep(2)
#######################
    saved_menu = driver.find_element(By.XPATH, '''//span[contains(text(), 'All posts')]''')
    saved_menu.click()
    print("Successfully navigated into saved posts col")
###########################
    time.sleep(2)
#######################
#########ittrated over the post ##############
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
    print(f"Found {total_posts} posts.")
    print(f"Found {total_posts} posts.")
    
    # Iterate over each post
    for i in range(total_posts):
        # if i == 0: continue
        posts = driver.find_elements(By.XPATH, posts_xpath)
        
        post = posts[i]
        href = post.get_attribute("href")
        
        # Skip if the URL doesn't look like a normal post URL
        if "/p/" not in href:
            print(f"Skipping post {i + 1} due to invalid URL: {href}")
            continue

        driver.execute_script("arguments[0].scrollIntoView(true);", post)
        post.click()
        time.sleep(5)
        
        print("\nClicked on:", post)
        print("Current URL before wait:", driver.current_url)
        
        # WebDriverWait(driver, 20).until(lambda d: d.current_url != posts_list_url)
        # print("Current URL after wait:", driver.current_url)
        print(f"Post {i + 1} URL: {driver.current_url}")
        
        # Go back to the posts list
        driver.back()
        
        # Wait until we are back on the posts list
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, posts_xpath))
        )
        time.sleep(2)
        print(f"---post no. {i}----------Process Ended-----------------\n\n")

#########ittrated over the post ##############
######################################################################################
    time.sleep(2)

    # time.sleep(500)
    # Optionally, wait for a while to simulate being on the saved posts page
except KeyboardInterrupt as e:
    print(" keyboard interrupt detected ")

finally:
    # Close the browser
    driver.quit()
    print("Completed successfully")
