from django.shortcuts import redirect, render, get_object_or_404
from estore.models import Category, Product, Cart
from django.contrib import messages
from datetime import date
import decimal
import requests
import json


headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <access-token>'
}

ACCOUNT_ID = '<account-id>'
CUSTOMER_ID = 000000


def is_authenticated():
    url = "https://api.freshbooks.com/auth/api/v1/users/me"
    response = requests.request("GET", url, headers=headers)
    if response.status_code == 200:
        return True
    return False    

def home(request):
    categories = Category.objects.filter()[:3]
    products = Product.objects.filter()[:8]
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'estore/index.html', context)


def category_products(request, url_slug):
    category = get_object_or_404(Category, url_slug=url_slug)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    context = {
        'category': category,
        'products': products,
        'categories': categories,
    }
    return render(request, 'estore/category_products.html', context)


def cart(request):
    cart_products = Cart.objects.all()

    amount = cart_total()
    shipping_amount = decimal.Decimal(0)

    context = {
        'cart_products': cart_products,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': amount + shipping_amount
    }
    return render(request, 'estore/cart.html', context)


def cart_total():
    amount = decimal.Decimal(0)
    cart_items = [item for item in Cart.objects.all()]
    if cart_items:
        for item in cart_items:
            temp_amount = (item.quantity * item.product.price)
            amount += temp_amount

    return amount


def add_to_cart(request):
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)

    item_already_in_cart = Cart.objects.filter(product=product_id)
    if item_already_in_cart:
        cart_item = get_object_or_404(Cart, product=product_id)
        cart_item.quantity += 1
        cart_item.save()
    else:
        Cart(product=product).save()

    return redirect('estore:cart')


def remove_from_cart(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
    return redirect('estore:cart')


def increment_cart(request, cart_id):
    if request.method == 'GET':
        cart_item = get_object_or_404(Cart, id=cart_id)
        cart_item.quantity += 1
        cart_item.save()        
    return redirect('estore:cart')


def decrement_cart(request, cart_id):
    if request.method == 'GET':
        cart_item = get_object_or_404(Cart, id=cart_id)
        if cart_item.quantity == 1:
            cart_item.delete()
        else:
            cart_item.quantity -= 1
            cart_item.save()
    return redirect('estore:cart')


def invoices(request):
    if not is_authenticated():
        return render(request, 'estore/no_auth.html')

    url = "https://api.freshbooks.com/accounting/account/5odNL6/invoices/invoices?include[]=lines&per_page=100"
    response = requests.request("GET", url, headers=headers)
    context = {
        'invoices': response.json()['response']['result']['invoices']
    }
    return render(request, 'estore/invoices.html', context)


def generate_invoice(request):
    if not is_authenticated():
        return render(request, 'estore/no_auth.html')

    url = "https://api.freshbooks.com/accounting/account/5odNL6/invoices/invoices?include[]=lines"
    today = date.today()
    payload = {
        "invoice": {
            "customerid": CUSTOMER_ID,
            "create_date": today.strftime("%Y-%m-%d"),
            "lines": []
        }
    }

    cart = Cart.objects.all()
    for item in cart:
        newItem = {"name": item.product.title, "qty": item.quantity, "unit_cost": {
            "amount": str(item.product.price), "code": "USD"}}
        payload['invoice']['lines'].append(newItem)
        item.delete()

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    messages.success(request, 'The invoice has been generated successfully using the Freshbooks API.')
    return redirect('estore:invoice', invoice_id=response.json()['response']['result']['invoice']['id'])


def invoice(request, invoice_id):
    if not is_authenticated():
        return render(request, 'estore/no_auth.html')

    url = "https://api.freshbooks.com/accounting/account/5odNL6/invoices/invoices/"+invoice_id+"?include[]=lines"
   
    response = requests.request("GET", url, headers=headers)

    context = {
        'invoice': response.json()['response']['result']['invoice']
    }
    return render(request, 'estore/invoice.html', context)


def email(request, invoice_id):
    url = "https://api.freshbooks.com/accounting/account/"+ACCOUNT_ID+"/invoices/invoices/"+invoice_id

    payload = json.dumps({
        "invoice": {
            "email_recipients": [
               request.POST.get('email')
            ]    
        ,
        "action_email": True
        }
    })
    
    response = requests.request("PUT", url, headers=headers, data=payload)

    messages.success(request, 'The email has been sent successfully using the Freshbooks API.')
    return redirect('estore:invoice', invoice_id=invoice_id)


def payment(request, invoice_id):
    url = "https://api.freshbooks.com/accounting/account/"+ACCOUNT_ID+"/payments/payments"

    today = date.today()
    payload = json.dumps({
        "payment": {
            "invoiceid": invoice_id,
            "amount": {
                "amount": request.POST.get('amount')
            },
        "date": today.strftime("%Y-%m-%d")
        }
    })
    
    response = requests.request("POST", url, headers=headers, data=payload)

    messages.success(request, 'The payment has been recorded successfully using the Freshbooks API.')
    return redirect('estore:invoice', invoice_id=invoice_id)
