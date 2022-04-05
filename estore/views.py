from django.shortcuts import redirect, render, get_object_or_404
from estore.models import Category, Product, Cart
import requests
import json
from django.contrib import messages
import decimal


headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <access-token>'
}


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
    url = "https://api.freshbooks.com/accounting/account/5odNL6/invoices/invoices?include[]=lines"
    response = requests.request("GET", url, headers=headers)
    context = {
        'invoices': response.json()['response']['result']['invoices']
    }
    return render(request, 'estore/invoices.html', context)


def generate_invoice(request):
    url = "https://api.freshbooks.com/accounting/account/5odNL6/invoices/invoices?include[]=lines"
    payload = {
        "invoice": {
            "customerid": 326310,
            "create_date": "2022-03-01",
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

    url = "https://api.freshbooks.com/accounting/account/5odNL6/invoices/invoices/"+invoice_id+"?include[]=lines"
   
    response = requests.request("GET", url, headers=headers)

    context = {
        'invoice': response.json()['response']['result']['invoice']
    }
    return render(request, 'estore/invoice.html', context)


def invoice2(request):

    url = "https://api.freshbooks.com/accounting/account/5odNL6/invoices/invoices?include[]=lines"
   
    payload = {
        "invoice": {
            "customerid": 326310,
            "create_date": "2022-03-01",
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

    #invid = response.json()['response']['result']['invoice']['invoiceid']
    #print(invid)
    print(response.json()['response'])

    payload2 = json.dumps({
        "invoice": {
            # "email_recipients": [
            #   "recipient_email@gmail.com"
            # ],
            # "invoice_customized_email": {
            #   "subject": "<YOUR COMPANY NAME> has sent you an invoice (0000027)",
            #   "body": "<YOUR COMPANY NAME> sent you invoice (0000027) for <INVOICE AMOUNT> that's due on <DUE DATE>"
            # },
            "action_email": True
        }
        })
    url2 = f"https://api.freshbooks.com/accounting/account/5odNL6/invoices/invoices/{invid}"
    print(url2)

    response2 = requests.request("PUT", url2, headers=headers, data=payload2)

    print("response",response2.json())

    messages.success(request, 'The invoice has been generated successfully using the Freshbooks API.')
    context = {'invoice': response.json()['response']['result']['invoice'], 'email': response2.json()['response']['result']['invoice'] }
    return render(request, 'estore/invoice.html', context)

