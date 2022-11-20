
from django.urls import path
from . import views

urlpatterns = [
    path('route/', views.RouteWithoutID),
    path('route/<int:id>/', views.RouteWithID),
    path('route/<int:id>/optimize/', views.RealtimeRoute),
    path('', views.Map)
]