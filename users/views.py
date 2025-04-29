from django.shortcuts import get_object_or_404, render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from accounts.models import User
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import Product, Cart
from doctors.models import Doctor,ProductRecommendation
import pandas as pd
from . models import DoctorBooking

from .models import  Doctor
from .forms import DoctorBookingForm

from .models import ProductReview
from .forms import ProductReviewForm

# Create your views here.




def about(request):
    return render(request,'about,html')


def contact(request):
    return render(request,'contact,html')

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib import messages
# from .models import UserProfile
User = get_user_model()


def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        age = request.POST['age']
        place = request.POST['place']
        contact_number = request.POST['contact_number']
        image = request.FILES.get('user_image')
        gender = request.POST['gender']

        errors = {}

        if User.objects.filter(username=username).exists():
            errors['username'] = "Username already exists!"

        try:
            validate_email(email)
        except ValidationError:
            errors['email'] = "Invalid email format!"

        if User.objects.filter(email=email).exists():
            errors['email'] = "Email already exists!"

        if UserProfile.objects.filter(contact_number=contact_number).exists():
            errors['contact_number'] = "This contact number is already registered!"

        if password != confirm_password:
            errors['password'] = "Passwords do not match!"

        if errors:
            return render(request, 'users/register.html', {'errors': errors})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = True
        user.save()

        UserProfile.objects.create(
            user=user,
            age=age,
            place=place,
            contact_number=contact_number,
            image=image,
            gender=gender
        )

        messages.success(request, "Registration successful! You can now log in.")
        return redirect('login')

    return render(request, 'users/register.html')

@login_required
@never_cache
def user_home_page(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()
    return render(request, 'users/home.html', {'products': products, 'query': query})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Review
from .forms import ReviewForm

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', product_id=product.id)

    else:
        form = ReviewForm()

    return render(request, 'users/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import Cart, Product

@login_required
@never_cache
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)

    if not created:
        cart_item.quantity += 1  # Increase quantity if already in cart
        cart_item.save()
    
    return redirect('cart')  # Redirect to cart page

@login_required
@never_cache
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_amount = sum(item.total_price() for item in cart_items)
    
    return render(request, 'users/cart.html', {'cart_items': cart_items, 'total_amount': total_amount})

@login_required
@never_cache
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')

@login_required
@never_cache
def update_cart_quantity(request, item_id, action):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    if action == "increase":
        cart_item.quantity += 1
    elif action == "decrease" and cart_item.quantity > 1:
        cart_item.quantity -= 1
    cart_item.save()
    return redirect('cart')

@login_required
@never_cache
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_amount = sum(item.total_price() for item in cart_items)

    if request.method == 'POST':
        cart_items.delete()  # Clear cart after purchase
        return render(request, 'users/checkout_success.html', {'total_amount': total_amount})

    return render(request, 'users/checkout_success.html', {'cart_items': cart_items, 'total_amount': total_amount})


# Load the dataset
skincare = pd.read_csv('./export_skincare.csv')


# Function to get skincare recommendations based on skin type
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import pandas as pd

# Function to get skincare recommendations based on skin type
def skincare_by_skin_type(skin_type, num_products):
    file_path = "export_skincare.csv"  # Update with the correct path
    df = pd.read_csv(file_path)

    df_filtered = df[df['skintype'].str.contains(skin_type, case=False, na=False)]
    recommended_products = df_filtered.head(num_products).to_dict(orient="records")

    return recommended_products


@login_required
def skincare_recommendation_view(request):
    doctors = Doctor.objects.all()

    if request.method == 'POST':
        skin_type = request.POST.get('skin_type', '').strip()
        num_products = int(request.POST.get('num_products', 5))
        recommendations = skincare_by_skin_type(skin_type, num_products)

        request.session['skincare_recommendations'] = recommendations  # Store in session
        return redirect('skincare_results')  # Redirect to the new results page

    return render(request, 'users/skincare.html', {'doctors': doctors})


@login_required
def skincare_results_view(request):
    recommendations = request.session.get('skincare_recommendations', [])
    doctors = Doctor.objects.all()  # Fetch doctors for dropdown

    return render(request, 'users/skincare_results.html', {'recommendations': recommendations, 'doctors': doctors})

@login_required
def user_product_status_view(request):
    user_recommendations = ProductRecommendation.objects.filter(user=request.user)
    return render(request, 'users/product_status.html', {'user_recommendations': user_recommendations})

def about_page(request):
    return render(request, 'users/about.html')

def contact_page(request):
    return render(request, 'users/contact.html')



@login_required
def book_doctor_view(request):
    if request.method == "POST":
        form = DoctorBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            messages.success(request, "Appointment request sent successfully!")
            return redirect('user_appointments')
    else:
        form = DoctorBookingForm()
    
    doctors = Doctor.objects.all()
    return render(request, 'users/book_doctor.html', {'form': form, 'doctors': doctors})


@login_required
def user_appointments_view(request):
    user_bookings = DoctorBooking.objects.filter(user=request.user)
    return render(request, 'users/appointments.html', {'user_bookings': user_bookings})


def product_reviews_view(request):
    products = Product.objects.all()  
    categories = Product.objects.values_list('category__name', flat=True).distinct()

    category = request.GET.get('category', '')  
    min_price = request.GET.get('min_price', '')  
    max_price = request.GET.get('max_price', '')  

    if category:
        products = products.filter(category=category)  

    if min_price:
        products = products.filter(price__gte=min_price)  

    if max_price:
        products = products.filter(price__lte=max_price)  

    return render(request, 'users/product_reviews.html', {'products': products, 'categories': categories})

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')

@login_required
def view_doctors(request):
    doctors = Doctor.objects.all()  # Fetch all registered doctors
    return render(request, 'users/view_doctors.html', {'doctors': doctors})


@login_required
def user_profile(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'users/profile.html', {'profile': profile})