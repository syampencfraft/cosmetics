from django.urls import path
from . import views

urlpatterns = [
    path('user_home/', views.user_home_page, name='user_home'),
    path('user_register/', views.register_user, name='user_register'),
    path('skincare/', views.skincare_recommendation_view, name='skincare_recommendation'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout',views.checkout,name='checkout'),
    path('user_product_status_view', views.user_product_status_view, name='user_product_status_view'),
    path('about/', views.about_page, name='about'),
    path('contact/', views.contact_page, name='contact'),

]
