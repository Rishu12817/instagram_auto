from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Set the path to your ChromeDriver executable
chrome_driver_path = 'C:\\chromedriver-win64\\chromedriver.exe'

# Set the user data directory
user_data_dir = 'C:\\selenium\\ChromeProfile'

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument(f'--user-data-dir={user_data_dir}')

# Create a new instance of the Chrome driver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open a website
driver.get('https://www.google.com')

# You can now use the driver to interact with the browser
# For example, searching for something on Google
search_box = driver.find_element(By.NAME, 'q')
search_box.send_keys('Selenium WebDriver')
search_box.submit()

# Don't forget to close the browser when done
driver.quit()

