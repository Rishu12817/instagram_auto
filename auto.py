from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# This will use your default browser (e.g., Chrome) if the driver is in PATH
driver = webdriver.Chrome()  # Or use webdriver.Firefox() for Firefox

driver.get("https://www.google.com")

# Optional: Keep the browser open for a while
input("Press Enter to close the browser...")
driver.quit()
