from django.shortcuts import render
from django.views import View

from recaptcha_solve.forms import LoginForm

from selenium import webdriver
from selenium.webdriver.common.by import By
from .forms import LoginForm

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
            
            print('\n', email, password, '\n')

            # configure selenium webdriver
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            driver = webdriver.Chrome(options=options)
            driver.get('https://www.kleinanzeigen.de/m-einloggen.html')

            # fill login form
            email_input = driver.find_element('login-email')
            email_input.send_keys(email)
            password_input = driver.find_element('login-password')
            password_input.send_keys(password)
            submit_button = driver.find_element('login-submit')
            submit_button.click()
        
    
    

