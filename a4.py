from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

# Set up the Service object with the path to the updated chromedriver
service = Service('C:/chromedriver-win64/chromedriver.exe')  # Updated path to the new ChromeDriver

# Set up Chrome options
options = Options()
options.add_argument('--start-maximized')

# Set up the WebDriver with the Service object
driver = webdriver.Chrome(service=service, options=options)

# Open Google
driver.get("https://www.google.com")

# Wait until the Google Apps icon is present
try:
    google_apps_icon = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Google apps']"))
    )

    # Click on the Google Apps icon
    ActionChains(driver).move_to_element(google_apps_icon).click().perform()

    # Wait for the Google Apps menu to open (you can adjust this to check for any specific menu item)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Gmail']"))  # Wait for Gmail option to load
    )

finally:
    # Close the browser
    driver.quit()
