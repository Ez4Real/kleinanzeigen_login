import time
import requests
import os


from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.http import HttpResponse
from django.contrib import messages

from recaptcha_solve.forms import reCAPTCHA

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys

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

class KleinanzeigenLogin(View):

    def get(self, request):
        
        page_url = settings.LOGIN_PAGE_URL

        # Load the website and perform necessary actions
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        # options.add_argument("--headless")  
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome(options=options)
        
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
               )
        # driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + 't')
        driver.get(page_url)
        
        delay()
        
        # Close Kleinanzeigen modals
        # button_click(driver, By.CLASS_NAME, 'Button-secondary')
        # button_click(driver, By.ID, 'gdpr-banner-accept')
        
        # Perform actions required to reach the audio captcha page
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
        response = requests.get(audio_el.get_attribute('href'))
        
        delay()
        
        mp3_path = 'audio.mp3'
        wav_path = 'audio.wav'
        
        download_audiofile(response, mp3_path)
        AudioSegment.converter = settings.FFMPEG_PATH
        convert_to_wav(mp3_path, wav_path)
        request.session['recognized_text'] = speech_recognition(wav_path)

        # Save the HTML page
        html_content = driver.page_source
        cookies = driver.get_cookies()
        
        driver.quit()
        
        return render(request, 'login.html', 
                      {'form': reCAPTCHA()})

        # # Pass the audio file and captcha form to the template
        # context = {
        #     'audio_url': 1,
        #     'captcha_form': 2  # Replace YourForm with your actual form class
        # }
        
        # Load a URL in the new tab
        # driver.get(page_url)
        
        # page_source = driver.page_source
        
        # # Quit the WebDriver
        # driver.quit()
        
        # return HttpResponse(page_source, content_type='text/html')

    def post(self, request):
        form = reCAPTCHA(request.POST)
        
        recognized_text = request.session.get('recognized_text')
        
        if form.is_valid():
            captcha_key = form.cleaned_data['captcha_key']
            
            print('\n', recognized_text, '\n')
            
            if captcha_key.lower() == recognized_text.lower():
                messages.success(request, 'Success! Captcha key is correct.')
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