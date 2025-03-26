from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_doctor, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_page, name='home_page')
]
