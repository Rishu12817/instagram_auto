from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# Set up the Service object with the path to chromedriver
service = Service('C:/chromedriver_win32/chromedriver.exe')  # Updated path

# Set up the WebDriver with the Service object
driver = webdriver.Chrome(service=service)

# Open Google
driver.get("https://www.google.com")

# Wait for the page to load
time.sleep(2)

# Find and click the Gmail icon
gmail_icon = driver.find_element(By.XPATH, '//a[@href="https://mail.google.com"]')
ActionChains(driver).move_to_element(gmail_icon).click().perform()

# Wait for Gmail to load
time.sleep(5)

# Close the browser
driver.quit()
