from django.urls import path
from . import views


app_name = 'estore'


urlpatterns = [
    path('', views.home, name="home"),
    
    path('cart/', views.cart, name="cart"),
    path('add-to-cart/', views.add_to_cart, name="add-to-cart"),
    path('remove-from-cart/<int:cart_id>/', views.remove_from_cart, name="remove-from-cart"),
    path('increment-cart/<int:cart_id>/', views.increment_cart, name="increment-cart"),
    path('decrement-cart/<int:cart_id>/', views.decrement_cart, name="decrement-cart"),
    
    path('invoices/', views.invoices, name="invoices"),
    path('invoice/', views.generate_invoice, name="generate-invoice"),
    path('invoice/<invoice_id>', views.invoice, name="invoice"),
    path('email/<invoice_id>', views.email, name="email"),
    path('payment/<invoice_id>', views.payment, name="payment"),

    path('<slug:url_slug>/', views.category_products, name="category-products")
]