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

# Wait until the Gmail icon is present
try:
    stay_out = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Stay signed out']")))
    # menu_icon = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[@aria-label="Gmail"]'))
    # menu_icon = WebDriverWait(driver, 10).until(
    # EC.presence_of_element_located((By.XPATH, "//svg[contains(@class, 'gb_E')]")))
    menu_icon = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//svg[@class='gb_E']")))

    # <button aria-label="Stay signed out" class="M6CB1c rr4y5c" jsname="ZUkOIc" jslog="71121; track:click;" data-dismiss="n">Stay signed out</button>
    # Click on the Gmail icon
    ActionChains(driver).move_to_element(stay_out).click().perform()
    ActionChains(driver).move_to_element(menu_icon).click().perform()

    # Wait for Gmail to load
    time.sleep(5)

finally:
    # Close the browser
    driver.quit()
