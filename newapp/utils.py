import json

from .models import *


def cookieCart(request):
    if 'cart' in request.COOKIES:
        cart = json.loads(request.COOKIES['cart'])
    else:
        cart = {}
    print('Cart: ', cart)
    order = {
        'get_cart_total': 0,
        'get_cart_items': 0,
        'shipping': False
    }
    items = []
    cartItems = order['get_cart_items']

    for i in cart:
        cartItems += int(cart[i]['quantity'])
        product = Product.objects.filter(id=i).first()

        if product is not None:
            total = product.price * int(cart[i]['quantity'])

            order['get_cart_items'] += int(cart[i]['quantity'])
            order['get_cart_total'] += total

            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL
                },
                'quantity': cart[i]['quantity'],
                'get_total': total
            }
            items.append(item)

            if not product.digital:
                order['shipping'] = True

    return {'cartItems': cartItems, 'order': order, 'items': items}


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        order = cookieData['order']
        items = cookieData['items']
        cartItems = cookieData['cartItems']

    return {'cartItems': cartItems, 'order': order, 'items': items}


def guestOrder(request, data):
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(
        email=email,
    )
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer=customer,
        complete=False
    )

    for item in items:
        product = Product.objects.filter(id=item['product']['id']).first()
        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity']
        )

    return customer, order
