import time
import requests
import os

from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.http import HttpResponse
from django.contrib import messages
from django.core.cache import cache

from recaptcha_solve.forms import reCAPTCHA
from http.cookies import SimpleCookie

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement

from selenium_stealth import stealth
import speech_recognition as sr
from pydub import AudioSegment

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
   
def field_fill(driver: webdriver.Chrome,
               query_str: str,
               cred_str: str) -> None:
    email_input: WebElement = find_element(driver, By.ID, query_str)
    email_input.send_keys(cred_str)
    
def download_audiofile(response, path) -> None:
    with open(path, "wb") as f:
        f.write(response.content)
        
def convert_to_wav(mp3_path, wav_path):
        audio = AudioSegment.from_mp3(mp3_path)
        audio.export(wav_path, format="wav")
                
def speech_recognition(audio_file) -> str:
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    return r.recognize_google(audio, language='en-EN')

class Chromchik():
    def __init__(self) -> None:
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        # options.add_argument("--headless")  
        # ???
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(options=options)
        
    def get_cookies(self):
        return self.driver.get_cookies()
        

class KleinanzeigenLogin(View):
    def __init__(self):
        self.html_content = None
        self.cookies = None

    def get(self, request):
        
        page_url = settings.LOGIN_PAGE_URL
        
        # chrome_options = webdriver.ChromeOptions()
        # # chrome_options.add_argument("--headless")  # Run Chrome in headless mode

        # # Load the website and perform necessary actions
        # chrome_driver = webdriver.Chrome(options=chrome_options)
        # chrome_driver.get(page_url)
        
        # cookies = chrome_driver.get_cookies()
        # print('\n', cookies, '\n')
        
        # chrome_driver.quit()

        # Load the website and perform necessary actions
        chrome = Chromchik()
        
        stealth(chrome.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
               )
        # chrome.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + 't')
        chrome.driver.get(page_url)
        
        
        # Save the HTML page and cookies
        cache.set('html_content', chrome.driver.page_source)
        
        print(chrome.get_cookies())
        # cache.set('cookies', chrome.driver.get_cookies())
        # cookies = chrome.driver.get_cookies()
        # print('\n', cookies, '\n')
        
        delay()
        
        # Close Kleinanzeigen modals
        # button_click(chrome.driver, By.CLASS_NAME, 'Button-secondary')
        # button_click(chrome.driver, By.ID, 'gdpr-banner-accept')
        
        # Perform actions required to reach the audio captcha page
        frames = chrome.driver.find_elements(By.TAG_NAME, "iframe")
        
        chrome.driver.switch_to.frame(frames[0])
        button_click(chrome.driver, By.CLASS_NAME, 'recaptcha-checkbox')
        delay()
        
        chrome.driver.switch_to.default_content()
        chrome.driver.switch_to.frame(frames[2])
        button_click(chrome.driver, By.CLASS_NAME, 'rc-button-audio')
        delay()
        
        # Get reCAPTCHA audio file
        audio_el = find_element(chrome.driver, By.CLASS_NAME, 'rc-audiochallenge-tdownload-link')
        response = requests.get(audio_el.get_attribute('href'))
        delay()
    
        mp3_path = 'audio.mp3'
        wav_path = 'audio.wav'
        download_audiofile(response, mp3_path)
        delay()
        
        AudioSegment.converter = settings.FFMPEG_PATH
        convert_to_wav(mp3_path, wav_path)
        recognized_text = speech_recognition(wav_path)
        cache.set('recognized_text', recognized_text.lower())
        
        print('\n', recognized_text, '\n')

        delay()
        
        chrome.driver.quit()
        
        return render(request, 'login.html', 
                      {'form': reCAPTCHA()})

    def post(self, request):
        form = reCAPTCHA(request.POST)
        recognized_text = cache.get('recognized_text')
        
        html_content = cache.get('html_content')
        html_content = html_content.replace('src="/recaptcha/api.js"', 'src="https://www.google.com/recaptcha/api.js"')
        # print('\n', html_content, '\n')
        
        # cookies = cache.get('cookies')
        # print('\n', cookies, '\n')
        
        
        if form.is_valid():
            captcha_key = form.cleaned_data['captcha_key']
            
            if captcha_key.lower() == recognized_text:
                messages.success(request, 'Success! Captcha key is correct.')
                
                delay()
                response = HttpResponse(html_content, content_type='text/html')
                # response.cookies.update(cookies)
                
                return response
                # return render(request, 'captcha.html', {})
            else:
                messages.error(request, 'Error! Captcha key is incorrect.')
        
        return render(request, 'login.html', 
                      {'form': form})
        
def download_audio(request):
    audio_file = 'audio.mp3'
    
    if os.path.exists(audio_file):
        with open(audio_file, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f"attachment; filename={audio_file}"
        return response
    else:
        return HttpResponse("File not found, Please try again.", status=404)