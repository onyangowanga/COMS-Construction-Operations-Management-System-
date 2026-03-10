"""
Core URL Configuration
Routes for template views (login, register, dashboard)
"""
from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home_view, name='home'),
    
    # Authentication Pages (Templates)
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Health Check
    path('health/', views.health_check, name='health_check'),
]
