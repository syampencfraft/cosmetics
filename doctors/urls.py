from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_doctor, name='register'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_page, name='home_page'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('about/', views.doctor_dashboard, name='about'),
    path('contact/', views.doctor_dashboard, name='contact'),

]
