import time
import os
import urllib.request

from django.views import View
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium_stealth import stealth

from recaptcha_solve.forms import reCAPTCHA

def delay() -> None:
    time.sleep(1.5)

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
   
def input_fill(driver: webdriver.Chrome,
               query_str: str,
               fill_str: str) -> None:
    input: WebElement = find_element(driver, By.ID, query_str)
    input.send_keys(fill_str)
        
        
def download_audio(request):
    if os.path.exists(mp3_path):
        with open(mp3_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f"attachment; filename={mp3_path}"
        return response
    else:
        return HttpResponse("File not found, Please try again.", status=404)
        
class KleinanzeigenLogin(View):
    def get(self, request):
        
        page_url = settings.LOGIN_PAGE_URL
        
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("detach", True)
        
        global driver
        driver = webdriver.Chrome(options=options, keep_alive=True)
        
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
               )
        
        driver.get(page_url)
        
        # # Perform actions required to reach the audio captcha page
        global frames
        frames = driver.find_elements(By.TAG_NAME, "iframe")
        
        driver.switch_to.frame(frames[0])
        button_click(driver, By.CLASS_NAME, 'recaptcha-checkbox')
        delay()
        
        driver.switch_to.default_content()
        driver.switch_to.frame(frames[2])
        button_click(driver, By.CLASS_NAME, 'rc-button-audio')
        delay()
        
        # Get reCAPTCHA audio file
        audio_el = find_element(driver, By.CLASS_NAME, 'rc-audiochallenge-tdownload-link')

        global mp3_path
        mp3_path = 'audio.mp3'
        urllib.request.urlretrieve(audio_el.get_attribute('href'), mp3_path)
        delay()
        
        return render(request, 'login.html', 
                        {'form': reCAPTCHA()})

    def post(self, request):
        form = reCAPTCHA(request.POST)
        
        if form.is_valid():
            captcha_key = form.cleaned_data['captcha_key']
            
            delay()
            input_fill(driver, 'audio-response', captcha_key)
            delay()
            button_click(driver, By.ID, 'recaptcha-verify-button')
            delay()
            driver.switch_to.default_content()
            button_click(driver, By.ID, 'recaptcha-demo-submit')
        
        return render(request, 'login.html', 
                        {'form': form})