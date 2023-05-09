from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login(email, password):
    # Create a new Chrome browser instance
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run the browser in headless mode
    driver = webdriver.Chrome(options=options)

    # Navigate to the login page
    driver.get('https://www.kleinanzeigen.de/m-einloggen.html')

    # Wait for the email input field to appear and enter the email address
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'login-email'))
    )
    email_input.send_keys(email)

    # Wait for the password input field to appear and enter the password
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'login-password'))
    )
    password_input.send_keys(password)

    # Click the Recaptcha checkbox to open the Recaptcha