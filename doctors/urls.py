from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('register/', views.register_doctor, name='register'),
    path('login', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_page, name='home_page'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('about/', views.doctor_dashboard, name='about'),
    path('contact/', views.doctor_dashboard, name='contact'),
    path('doctor-history/', views.doctor_user_history_view, name='doctor_user_history'),
    path('doctor-appointments/', views.doctor_bookings_view, name='doctor_bookings'),



]
