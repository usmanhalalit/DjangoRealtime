from django.urls import path

from . import views

app_name = 'playground'

urlpatterns = [
    path('', views.test_page, name='test_page'),
    path('send-message/', views.send_test_message, name='send_message'),
]
