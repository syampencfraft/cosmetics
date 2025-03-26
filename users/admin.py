from django.contrib import admin
from .models import UserProfile, Category, Product, Cart
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)

