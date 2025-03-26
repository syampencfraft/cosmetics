from django.shortcuts import render
from .models import DoctorReg
from accounts.models import User
from users.models import UserProfile
import re
from django.shortcuts import render, redirect
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
# Create your views here.

def register_doctor(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        department = request.POST['department']
        description = request.POST['description']
        image = request.FILES.get('image')

        errors = {}

      
        if User.objects.filter(username=username).exists():
            errors['username'] = "Username already exists!"

     
        try:
            validate_email(email)
        except ValidationError:
            errors['email'] = "Invalid email format!"

  
        if User.objects.filter(email=email).exists():
            errors['email'] = "Email already exists!"

        if DoctorReg.objects.filter(department=department).exists():
            errors['department'] = "This department already has a doctor registered!"

  
        if password != confirm_password:
            errors['password'] = "Passwords do not match!"

        if errors:
            return render(request, 'doctors/register.html', {'errors': errors})

       
        user = User.objects.create_user(username=username, email=email, password=password, user_type='doctor')
        user.is_active = True
        user.save()

    
        DoctorReg.objects.create(
            user=user,
            department=department,
            description=description,
            image=image
        )

        messages.success(request, "Registration successful! Your account will be reviewed by an admin.")
        return redirect('register')

    return render(request, 'doctors/doctor_reg.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            if not user.is_active:
                messages.error(request, "Your account is pending approval by the admin.")
                return redirect('login')

            login(request, user)

            if user.is_superuser:  
                return redirect("admin_panel:admin_dashboard")  
            
            elif UserProfile.objects.filter(user=user).exists():
                messages.success(request, "Login successful! Welcome to your profile.")
                return redirect("user_home")

            elif DoctorReg.objects.filter(user=user).exists():  
                messages.success(request, "Login successful!")
                return redirect("home_page")

            else:
                messages.success(request, "Login successful!")
                return redirect("home_page")  

        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')

    return render(request, 'doctors/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')

@login_required
@never_cache
def home_page(request):
    return render(request, 'doctors/home.html')