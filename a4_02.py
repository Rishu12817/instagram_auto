from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

import config

# Set up the Service object with the path to the updated chromedriver
service = Service('C:/chromedriver-win64/chromedriver.exe')  # Updated path to the new ChromeDriver

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
###################### log in finishes ###################################

    google_apps_icon = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Google apps']"))
    )

    # Click on the Google Apps icon
    ActionChains(driver).move_to_element(google_apps_icon).click().perform()



    # Wait for the page to load after login (for example, checking if the profile page is accessible)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Your profile']"))
    )

    print("Login successful!")

    # Optionally, wait for a while to simulate being logged in
    time.sleep(5)

finally:
    # Close the browser
    driver.quit()
