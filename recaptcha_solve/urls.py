from django.urls import path
from recaptcha_solve import views

urlpatterns = [
    path('', views.login_view, name='login'),
]
