from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = 'chatroom'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='chatroom:login'), name='logout'),
    path('send-message/', views.send_message, name='send_message'),
    path('get-messages/', views.get_messages, name='get_messages'),
]
