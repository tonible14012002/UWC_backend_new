from django.urls import path, include
from django.http import HttpResponse
from . import views


urlpatterns = [
    path('auth/', views.login),
    path('', views.home),
    path('auth/refresh/', views.refresh),
]