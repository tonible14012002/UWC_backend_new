from django.urls import path, include
from django.http import HttpResponse
from . import views


urlpatterns = [
    path('auth/', views.login),
    path('auth/refresh/', views.refresh),
    path('employee/', views.employee),
    path('employee/<int:id>/', views.employee_detail),
    path('employee/<int:employee_id>/schedule/', views.schedule),
    path('employee/<int:employee_id>/schedule/<int:id>/', views.worktime_detail),
    
]