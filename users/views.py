from django.shortcuts import get_object_or_404, render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from accounts.models import User
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import Product, Cart
from doctors.models import Doctor,ProductRecommendation
# Create your views here.



def about(request):
    return render(request,'about,html')


def contact(request):
    return render(request,'contact,html')


def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        age = request.POST['age']
        place = request.POST['place']
        contact_number = request.POST['contact_number']
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

        if UserProfile.objects.filter(contact_number=contact_number).exists():
            errors['contact_number'] = "This contact number is already registered!"

        if password != confirm_password:
            errors['password'] = "Passwords do not match!"

        if errors:
            return render(request, 'users/register.html', {'errors': errors})

        user = User.objects.create_user(username=username, email=email, password=password, user_type='user')
        user.is_active = True
        user.save()

        UserProfile.objects.create(
            user=user,
            age=age,
            place=place,
            contact_number=contact_number,
            image=image
        )

        messages.success(request, "Registration successful! You can now log in.")
        return redirect('login')

    return render(request, 'users/register.html')

@login_required
@never_cache
def user_home_page(request):
    products = Product.objects.all() 
    return render(request, 'users/home.html', {'products':products})

@login_required
@never_cache
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'users/product_detail.html', {'product': product})

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
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_amount = sum(item.total_price() for item in cart_items)

    if request.method == 'POST':
        cart_items.delete()  # Clear cart after purchase
        return render(request, 'users/checkout_success.html', {'total_amount': total_amount})

    return render(request, 'users/checkout_success.html', {'cart_items': cart_items, 'total_amount': total_amount})

import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse

# Load the dataset
skincare = pd.read_csv('./export_skincare.csv')


# Function to get skincare recommendations based on skin type
def skincare_by_skin_type(skin_type, k=5):
    if not skin_type:  # Check if skin_type is None or empty
        return []
    skin_type = skin_type.capitalize()
    
    if skin_type not in skincare.columns:
        return []

    filtered_products = skincare[skincare[skin_type] == 1]
    recommendations = filtered_products[['product_name', 'notable_effects', 'product_href']].head(k).to_dict(orient='records')
    
    return recommendations



@login_required
def skincare_recommendation_view(request):
    recommendations = None
    doctors = Doctor.objects.all()

    if request.method == 'POST':
        skin_type = request.POST.get('skin_type', '').strip()
        num_products = int(request.POST.get('num_products', 5))
        recommendations = skincare_by_skin_type(skin_type, num_products)

        if 'send_to_doctor' in request.POST:
            product_name = request.POST.get('product_name')
            product_href = request.POST.get('product_href')
            notable_effects = request.POST.get('notable_effects')
            doctor_id = request.POST.get('doctor_id')

            doctor = Doctor.objects.get(id=doctor_id)
            ProductRecommendation.objects.create(
                user=request.user,
                product_name=product_name,
                product_href=product_href,
                notable_effects=notable_effects,
                doctor=doctor
            )
            return redirect('skincare_recommendation')

    return render(request, 'users/skincare.html', {'recommendations': recommendations, 'doctors': doctors})

@login_required
def user_product_status_view(request):
    user_recommendations = ProductRecommendation.objects.filter(user=request.user)
    return render(request, 'users/product_status.html', {'user_recommendations': user_recommendations})

def about_page(request):
    return render(request, 'users/about.html')

def contact_page(request):
    return render(request, 'users/contact.html')