import requests
import time
import os

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

import urllib.request

import speech_recognition as sr
from pydub import AudioSegment


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
            
            driver = webdriver.Firefox(keep_alive=True)
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
            
            time.sleep(3)
            
            driver.switch_to.default_content()
            frame = driver.find_element(By.XPATH, "//iframe[@title='reCAPTCHA-Aufgabe läuft in zwei Minuten ab']")
            frames.append(frame)
            
            driver.switch_to.frame(frame)
            
            button_click(driver, By.CLASS_NAME, 'rc-button-audio')
            time.sleep(2)
            
            
            button_click(driver, By.CLASS_NAME, 'rc-button-default')
            time.sleep(2)
            
            url = find_element(driver, By.CLASS_NAME, 'rc-audiochallenge-tdownload-link').get_attribute('href')

            response = requests.get(url)
            audio_path = "audio.mp3"
            wav_path = "audio.wav"
            with open(audio_path, "wb") as f:
                f.write(response.content)
                
            AudioSegment.converter = 'C:/ProgramData/chocolatey/bin/ffmpeg.exe'
            audio = AudioSegment.from_mp3(settings.BASE_DIR / 'audio.mp3')
            

            # Export the audio file in WAV format
            audio.export(wav_path, format="wav")
            
            r = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio = r.record(source)
            text = r.recognize_google(audio)
            
            print('\n', text)
            
            # button_click(driver, By.ID, 'login-submit')
            
            # wait for the next page to load
            # WebDriverWait(driver, 10).until(EC.url_contains('https://www.kleinan zeigen.de/m-meins.html'))

        return render(request, self.template_name, {'form': form})
        
