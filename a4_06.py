from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import config

# Set up the Service object with the path to the updated chromedriver
# service = Service('C:/chromedriver-win64/chromedriver.exe')  # Updated path to the new ChromeDriver
service = Service("C:\chromedriver-win64\chromedriver.exe")  # Updated path to the new ChromeDriver
# service = Service('C:/chromedriver-win64/chromedriver.exe')  # Updated path to the new ChromeDriver


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
        
    # # Now, construct the URL for the saved posts page
    # saved_posts_url = f"https://www.instagram.com/{config.cred['user']}/saved/"
    # # Navigate to the saved posts section
    # driver.get(saved_posts_url)
    # print(f"Successfully navigated to saved posts of user: {config.cred['user']}")


#######################
    burgur_menu = driver.find_element(By.XPATH, "//span[contains(text(), 'More')]")
    burgur_menu.click()
###########################
    time.sleep(5)
#######################
    saved_menu = driver.find_element(By.XPATH, "//span[contains(text(), 'Saved')]")
    saved_menu.click()
    print("Successfully navigated to saved posts")
###########################
    time.sleep(2)

    # time.sleep(500)
    # Optionally, wait for a while to simulate being on the saved posts page

finally:
    # Close the browser
    # driver.quit()
    print("Completed successfully")
