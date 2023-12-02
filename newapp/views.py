import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View

from .forms import LoginForm, SignUpForm, ProductForm, CustomerForm, OrderForm
from .models import *
import datetime

from .utils import cartData, guestOrder


# Create your views here.
class Store(View):
    def get(self, request, *args, **kwargs):
        if 'key' in request.GET:
            key = request.GET.get('key')
            products = Product.objects.filter(name__icontains=key)
        else:
            products = Product.objects.all()
        data = cartData(request)
        cartItems = data['cartItems']
        if len(products) == 0:
            messages.error(request, "No product")

        context = {
            'products': products,
            'cartItems': cartItems,
        }

        return render(request, 'store.html', context)


class Cart(View):
    def get(self, request, *args, **kwargs):
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


class Checkout(View):
    def get(self, request, *args, **kwargs):
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


class UpdateItem(View):
    def post(self, request, *args, **kwargs):
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


class ProcessOrder(View):
    def post(self, request, *args, **kwargs):
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
            return redirect('store')
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
            else:
                messages.error(request, 'Wrong username or password')
        context = {
            'form': form,
        }
        return render(request, 'login.html', context)


def sign_out(request):
    logout(request)
    return redirect('store')


class SignUpAPI(View):
    def get(self, request):
        form = SignUpForm()
        return JsonResponse({'form': form})


class SignUp(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('store')
        form = SignUpForm()
        return render(request, 'signup.html', {'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']

            user = User.objects.create_user(username=username, password=password, email=email)

            customer = Customer.objects.create(user=user, email=email)
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


class Detail(View):
    def get(self, request, *args, **kwargs):
        data = cartData(request)
        cartItems = data['cartItems']
        product = Product.objects.filter(id=kwargs.get('id')).first()
        context = {
            'product': product,
            'cartItems': cartItems
        }
        return render(request, 'detail.html', context)


class Manage(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            if 'key' in request.GET:
                key = request.GET.get('key')
                products = Product.objects.filter(name__icontains=key)
            else:
                products = Product.objects.all()

            data = cartData(request)
            cartItems = data['cartItems']
            context = {
                'products': products,
                'cartItems': cartItems
            }
            return render(request, 'admin_page.html', context)
        else:
            return custom_404(request)


class ManageCustomers(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            if 'key' in request.GET:
                key = request.GET.get('key')
                customers = Customer.objects.filter(name__icontains=key)
            else:
                customers = Customer.objects.all()
            data = cartData(request)
            cartItems = data['cartItems']
            context = {
                'customers': customers,
                'cartItems': cartItems
            }
            return render(request, 'customers_management.html', context)
        else:
            return custom_404(request)


class ManageOrders(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            if 'key' in request.GET:
                key = request.GET.get('key')
                orders = Order.objects.filter(Q(customer__name__icontains=key) | Q(id__icontains=key))
            else:
                orders = Order.objects.all()
            data = cartData(request)
            cartItems = data['cartItems']
            context = {
                'orders': orders,
                'cartItems': cartItems
            }
            return render(request, 'orders_management.html', context)
        else:
            return custom_404(request)

    def post(self, request, *args, **kwargs):
        pass


class ManageProduct(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            key = kwargs['id']
            product = Product.objects.filter(id=key).first()

            data = cartData(request)
            cartItems = data['cartItems']
            context = {
                'cartItems': cartItems,
                'image': product.imageURL
            }
            if product is not None:
                context['form'] = ProductForm(instance=product)
            else:
                messages.error(request, f"No product with id: {key}")
                return redirect('manager')

            return render(request, 'product_detail.html', context)
        else:
            return custom_404(request)

    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            key = kwargs['id']
            product = Product.objects.filter(id=key).first()
            if product is None:
                messages.error(request, f"No product with id: {key}")
                return redirect('manager')

            context = {}
            if 'save' in request.POST:
                form = ProductForm(request.POST, request.FILES, instance=product)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Product changed successfully")
                    return redirect('manager')
                context['form'] = form
                return render(request, 'product_detail.html', context)
            elif 'del' in request.POST:
                product.delete()
                messages.success(request, "Product deleted successfully")
                return redirect('manager')
        else:
            return custom_404(request)


class AddProduct(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            data = cartData(request)
            cartItems = data['cartItems']
            context = {'cartItems': cartItems, 'form': ProductForm, 'action': 'add'}
            return render(request, 'product_detail.html', context)
        else:
            return custom_404(request)

    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Product changed successfully")
                return redirect('manager')

        else:
            return custom_404(request)


class ManageCustomer(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            key = kwargs['id']
            customer = Customer.objects.filter(id=key).first()

            data = cartData(request)
            cartItems = data['cartItems']
            context = {
                'cartItems': cartItems,
            }
            if customer is not None:
                context['form'] = CustomerForm(instance=customer)
                context['orders'] = customer.order_set.all()
            else:
                messages.error(request, f"No customer with id: {key}")
                return redirect('customers_management')

            return render(request, 'customer_detail.html', context)
        else:
            return custom_404(request)

    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            key = kwargs['id']
            customer = Customer.objects.filter(id=key).first()
            if customer is None:
                messages.error(request, f"No customer with id: {key}")
                return redirect('customers_management')

            context = {}

            if 'save' in request.POST:
                form = CustomerForm(request.POST, request.FILES, instance=customer)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Customer changed successfully")
                    return redirect('customers_management')
                context['form'] = form
                return render(request, 'product_detail.html', context)
            elif 'del' in request.POST:
                customer.delete()
                messages.success(request, "customer deleted successfully")
                return redirect('customers_management')
        else:
            return custom_404(request)


class ManageOrder(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            key = kwargs['id']
            order = Order.objects.filter(id=key).first()

            data = cartData(request)
            cartItems = data['cartItems']
            context = {
                'cartItems': cartItems,
            }

            if order is not None:
                form = OrderForm(instance=order)
                form.fields['transaction_id'].disabled = True
                form.fields['complete'].disabled = True

                items = order.orderitem_set.all()
                context['items'] = items
                context['form'] = form
                context['order'] = order
            else:
                messages.error(request, f"No order with id: {key}")
                return redirect('orders_management')

            return render(request, 'order_detail.html', context)
        else:
            return custom_404(request)

    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            key = kwargs['id']
            order = Order.objects.filter(id=key).first()
            if order is None:
                messages.error(request, f"No customer with id: {key}")
                return redirect('orders_management')
            context = {}
            if 'save' in request.POST:
                form = OrderForm(request.POS, instance=order)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Order changed successfully")
                    return redirect('orders_management')
                context['form'] = form
                return render(request, 'order_detail.html', context)
            elif 'del' in request.POST:
                order.delete()
                messages.success(request, "Order deleted successfully")
                return redirect('orders_management')
        else:
            return custom_404(request)


class AddUser(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            data = cartData(request)
            cartItems = data['cartItems']
            context = {'cartItems': cartItems, 'form': SignUpForm, 'action': 'add'}
            return render(request, 'product_detail.html', context)
        else:
            return custom_404(request)

    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            form = SignUpForm(request.POST, request.FILES)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                email = form.cleaned_data['email']

                user = User.objects.create_user(username=username, password=password, email=email)

                customer = Customer.objects.create(user=user, email=email)
                if form.cleaned_data['name'] == '':
                    customer.name = username
                else:
                    customer.name = form.cleaned_data['name']
                customer.email = form.cleaned_data['email']
                customer.save()

                return redirect("orders_management")

            return render(request, 'product_detail.html', {'form': form})
        else:
            return custom_404(request)


class DeleteAPI(View):
    def get(self, request):
        pass

    def delete(self, request, *args, **kwargs):
        if request.user.is_staff:
            data = json.loads(request.body)
            if data['object'] == 'product':
                Product.objects.filter(id__in=data['ids']).delete()

            messages.success(request, "Delete selected")
            return JsonResponse({
                'res': "success",
                'list': data['ids']
            })

        else:
            return JsonResponse({
                'res': "No permission"
            })


def custom_404(request, exception=None):
    return render(request, 'custom_404.html', status=404)
