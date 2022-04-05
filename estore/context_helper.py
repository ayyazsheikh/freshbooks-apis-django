from .models import Category, Cart


def store_menu(request):
    categories = Category.objects.filter()
    context = {
        'categories_menu': categories,
    }
    return context


def cart_menu(request):
    cart_items = Cart.objects.all()
    context = { 'cart_items': cart_items }
    return context