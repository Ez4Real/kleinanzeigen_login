import time
import requests

from django.shortcuts import render
from django.views import View
from django.conf import settings

from recaptcha_solve.forms import LoginForm

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement

from .forms import LoginForm

import speech_recognition as sr
from pydub import AudioSegment


def delay() -> None:
    time.sleep(1)

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
    
    
def download_audio(response, path) -> None:
    with open(path, "wb") as f:
        f.write(response.content)
        
def convert_to_wav(mp3_path, wav_path):
                audio = AudioSegment.from_mp3(mp3_path)
                audio.export(wav_path, format="wav")
                
def speech_recognition(audio_file) -> str:
                r = sr.Recognizer()
                with sr.AudioFile(audio_file) as source:
                    audio = r.record(source)
                return r.recognize_google(audio, language='de-DE')

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
            
            driver = webdriver.Edge(keep_alive=True)
            driver.get(page_url)

            # Close modals
            button_click(driver, By.CLASS_NAME, 'Button-secondary')
            delay()
            button_click(driver, By.ID, 'gdpr-banner-accept')
            delay()
            
            # Fill log in fields
            field_fill(driver, 'login-email', email)
            field_fill(driver, 'login-password', password)
            delay()
            
            driver.switch_to.frame(driver.find_element(By.TAG_NAME, "iframe"))
        
            # # Get reCAPTCHA audio file
            button_click(driver, By.CLASS_NAME, 'recaptcha-checkbox')
            delay()
            
            driver.switch_to.default_content()
            
            driver.switch_to.frame(
                driver.find_element(By.XPATH, "//iframe[@title='reCAPTCHA-Aufgabe läuft in zwei Minuten ab']")
            )
            
            button_click(driver, By.CLASS_NAME, 'rc-button-audio')
            delay()
            
            audiofile = find_element(driver, By.CLASS_NAME, 'rc-audiochallenge-tdownload-link')

            response = requests.get(audiofile.get_attribute('href'))
            audio_path = "audio.mp3"
            wav_path = "audio.wav"
            
            download_audio(response, audio_path)
            delay()
            AudioSegment.converter = 'C:/ProgramData/chocolatey/bin/ffmpeg.exe'
            convert_to_wav(audio_path, wav_path)
            delay()
            
            
            field_fill(driver, 'audio-response', speech_recognition(wav_path))
            button_click(driver, By.ID, 'recaptcha-verify-button')
            delay()
            
            driver.switch_to.default_content()
            button_click(driver, By.ID, 'login-submit')
            delay()
            
            driver.close()

        return render(request, self.template_name, {'form': form})
        
