import json


from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View

from .forms import LoginForm, SignUpForm
from .models import *
import datetime

from .utils import cookieCart, cartData, guestOrder


# Create your views here.
def store(request):
    if 'key' in request.GET:
        key = request.GET.get('key')
        products = Product.objects.filter(name__icontains=key)
    else:
        products = Product.objects.all()
    data = cartData(request)
    cartItems = data['cartItems']

    context = {
        'products': products,
        'cartItems': cartItems,
    }

    return render(request, 'store.html', context)


def cart(request):
    data = cartData(request)
    order = data['order']
    items = data['items']
    cartItems = data['cartItems']

    context = {
        'order': order,
        'items': items,
        'cartItems': cartItems
    }

    return render(request, 'cart.html', context)


def checkout(request):
    data = cartData(request)
    order = data['order']
    items = data['items']
    cartItems = data['cartItems']
    context = {
        'order': order,
        'items': items,
        'cartItems': cartItems
    }

    return render(request, 'checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productID = data['productID']
    action = data['action']
    quantity = int(data['quantity'])

    customer = request.user.customer
    product = Product.objects.filter(id=productID).first()
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = orderItem.quantity + quantity
    elif action == 'remove':
        orderItem.quantity = orderItem.quantity - quantity

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()
    if order.shipping:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['country'],
            zipcode=data['shipping']['zipcode']
        )
    return JsonResponse({
        'res': "response"
    })


class Sign_In(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('')
        form = LoginForm()
        context = {
            'form': form
        }
        return render(request, 'login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('store')

        return render(request, 'login.html', {'form': form})


def sign_out(request):
    logout(request)
    return redirect('store')


class SignUp(View):
    def get(selfs, request):
        form = SignUpForm()
        return render(request, 'signup.html', {'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = User.objects.create_user(username=username, password=password)

            customer = Customer.objects.create(user=user)
            if form.cleaned_data['name'] == '':
                customer.name = username
            else:
                customer.name = form.cleaned_data['name']
            customer.email = form.cleaned_data['email']
            customer.save()

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('store')

        return render(request, 'signup.html', {'form': form})


def detail(request, slug, id):
    data = cartData(request)
    cartItems = data['cartItems']
    product = Product.objects.filter(id=id).first()
    context = {
        'product': product,
        'cartItems': cartItems
    }
    return render(request, 'detail.html', context)
