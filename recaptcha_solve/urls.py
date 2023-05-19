from django.urls import path
from recaptcha_solve import views

urlpatterns = [
    path('', views.KleinanzeigenLogin.as_view(), name='login'),
    path('download/', views.download_audio, name='download-audio'),
]
