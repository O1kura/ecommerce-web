from django.urls import path
from . import views
urlpatterns = [
    path('', views.Store.as_view(), name='store'),
    path('cart/', views.Cart.as_view(), name='cart'),
    path('checkout/', views.Checkout.as_view(), name='checkout'),
    path('update_item/', views.UpdateItem.as_view(), name='update'),
    path('process_order/', views.ProcessOrder.as_view(), name='process'),
    path('login/', views.Sign_In.as_view(), name='sign_in'),
    path('logout/', views.sign_out, name='sign_out'),
    path('<slug:slug>.<int:id>', views.Detail.as_view()),
    path('signup/', views.SignUp.as_view(), name='sign_up'),
    path('manager/', views.Manage.as_view(), name='manager'),
    path('manager/customers/', views.ManageCustomers.as_view(), name='customers_management'),
    path('manager/orders/', views.ManageOrders.as_view(), name='orders_management'),
    path('manager/products/<int:id>', views.ManageProduct.as_view()),
    path('manager/products/add', views.AddProduct.as_view())


]