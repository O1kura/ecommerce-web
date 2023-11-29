from django.urls import path
from . import views
urlpatterns = [
    path('', views.store, name='store'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('update_item/', views.updateItem, name='update'),
    path('process_order/', views.processOrder, name='process'),
    path('login/', views.Sign_In.as_view(), name='sign_in'),
    path('logout/', views.sign_out, name='sign_out'),
    path('<slug:slug>.<int:id>', views.detail),
    path('signup/', views.SignUp.as_view(), name='sign_up')
]