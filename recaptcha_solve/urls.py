from django.urls import path
from recaptcha_solve import views

urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
]
