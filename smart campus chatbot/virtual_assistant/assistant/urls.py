from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('get-response/', views.get_response, name='get_response'),
    path('get_response/', views.get_response, name='get_response'),
]