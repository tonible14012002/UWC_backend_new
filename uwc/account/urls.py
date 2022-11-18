from django.urls import path, include
from django.http import HttpResponse
from . import views


urlpatterns = [
    path('auth/', views.login),
    path('auth/refresh/', views.refresh),
    path('', views.home),
]