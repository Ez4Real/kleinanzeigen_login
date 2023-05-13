import requests
import time

from django.shortcuts import render
from django.views import View
from django.conf import settings

from recaptcha_solve.forms import LoginForm

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


from .forms import LoginForm

from selenium.webdriver.remote.webelement import WebElement


def find_element(driver: webdriver.Chrome,
                 attr_literal: str,
                 query_str: str) -> None:
    return WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((attr_literal, query_str))
    )

def button_click(driver: webdriver.Chrome,
                 attr_literal: str,
                 query_str: str) -> None:
    element_to_click: WebElement = find_element(driver, attr_literal, query_str)
    ActionChains(driver).move_to_element(element_to_click).click().perform()
   
    
def field_fill(driver: webdriver.Chrome,
               query_str: str,
               cred_str: str) -> None:
    email_input: WebElement = find_element(driver, By.ID, query_str)
    email_input.send_keys(cred_str)


class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            # retrieve form data
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # configure selenium webdriver
            page_url = settings.LOGIN_PAGE_URL
            # page_url = 'https://www.google.com/recaptcha/api2/demo'
            
            driver = webdriver.Chrome()
            driver.get(page_url)

            # Close modals
            button_click(driver, By.CLASS_NAME, 'Button-secondary')
            button_click(driver, By.ID, 'gdpr-banner-accept')
            
            # Fill log in fields
            field_fill(driver, 'login-email', email)
            field_fill(driver, 'login-password', password)
            
            frames = []
            frame = driver.find_element(By.TAG_NAME, "iframe")
            frames.append(frame)
            
            driver.switch_to.frame(frame)
        
            # Get reCAPTCHA audio file
            button_click(driver, By.CLASS_NAME, 'recaptcha-checkbox')
            
            driver.switch_to.default_content()
            frame = driver.find_element(By.XPATH, "//iframe[@title='reCAPTCHA-Aufgabe läuft in zwei Minuten ab']")
            frames.append(frame)
            
            
            driver.switch_to.frame(frame)
            
            button_click(driver, By.CLASS_NAME, 'rc-button-audio')
            button_click(driver, By.CLASS_NAME, 'rc-button-default')
            
            download = find_element(driver, By.CLASS_NAME, 'rc-audiochallenge-tdownload-link')
            print(download.get_attribute('src'))
            

            # solver = TwoCaptcha(settings.API_KEY)
            
            # print('\n', solver.balance())
        

            # try:
            #     result = solver.recaptcha(
            #         sitekey=settings.DATA_SITE_KEY,
            #         url=settings.LOGIN_PAGE_URL)

            # except Exception as e:
            #     print("An exception occurred while solving the CAPTCHA:")
            #     print("Error type:", type(e).__name__)
            #     print("Error message:", str(e))

            # else:
            #     print('solved: ' + str(result))
            
            # response = requests.post('https://captchasolver.com/api/recaptcha',
            #                          json={
            #     "url": settings.LOGIN_PAGE_URL,
            #     "apikey": settings.API_KEY,
            #     "sitekey": settings.DATA_SITE_KEY
            # })

            # if response.ok:
            #     result = response.json()
            #     if result['status'] == 1:
            #         print('CAPTCHA solved: {}'.format(result['solution']['gRecaptchaResponse']))
            #     else:
            #         print('CAPTCHA was not solved')
            # else:
            #     print('Error occurred while solving CAPTCHA: {}'.format(response.text))
                
                
            
            
            

            # Submit the login form with the ReCAPTCHA response
            # login_data = {
            #     'username': 'myusername',
            #     'password': 'mypassword',
            #     'g-recaptcha-response': captcha_response
            # }
            # login_response = requests.post(page_url, data=login_data)
            
            
            # button_click(driver, By.ID, 'login-submit')
            
            # wait for the next page to load
            WebDriverWait(driver, 10).until(EC.url_contains('https://www.kleinanzeigen.de/m-meins.html'))

        return render(request, self.template_name, {'form': form})
        
