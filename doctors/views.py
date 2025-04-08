from django.shortcuts import render
# from .models import DoctorReg
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
from .models import Doctor, ProductRecommendation
from django.shortcuts import render, get_object_or_404
from users.models import DoctorBooking  #



# Create your views here.
def index(request):
    return render(request,'doctors/index.html')



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
            return render(request, 'doctors/doctor_reg.html', {'errors': errors})

       
        user = User.objects.create_user(username=username, email=email, password=password, user_type='doctor')
        user.is_active = True
        user.save()

    
        Doctor.objects.create(
            user=user,
            department=department,
            description=description,
            profile_image=image
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

            elif Doctor.objects.filter(user=user).exists():  
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

@login_required
def doctor_dashboard(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, "You are not registered as a doctor.")
        return redirect('home_page')  # Redirect to a relevant page

    pending_requests = ProductRecommendation.objects.filter(doctor=doctor, status='pending')

    if request.method == 'POST':
        recommendation_id = request.POST.get('recommendation_id')
        action = request.POST.get('action')

        recommendation = ProductRecommendation.objects.get(id=recommendation_id)

        if action == 'approve':
            recommendation.status = 'approved'
        elif action == 'reject':
            recommendation.status = 'rejected'
        
        recommendation.save()
        return redirect('doctor_dashboard')

    return render(request, 'doctors/dashboard.html', {'pending_requests': pending_requests})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ProductRecommendation

@login_required
def doctor_user_history_view(request):
    if not hasattr(request.user, 'doctor'):
        return render(request, 'doctors/not_authorized.html')

    # Fetch past user requests for the logged-in doctor
    user_requests = ProductRecommendation.objects.filter(doctor=request.user.doctor).order_by('-created_at')

    return render(request, 'doctors/user_history.html', {'user_requests': user_requests})


@login_required
def doctor_bookings_view(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, "You are not registered as a doctor.")
        return redirect('home_page')

    bookings = DoctorBooking.objects.filter(doctor=doctor)

    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        action = request.POST.get("action")

        booking = DoctorBooking.objects.get(id=booking_id)

        if action == "approve":
            booking.status = "approved"
        elif action == "reject":
            booking.status = "rejected"
        
        booking.save()
        return redirect('doctor_bookings')

    return render(request, 'doctors/appointments.html', {'bookings': bookings})

