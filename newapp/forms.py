from django import forms
from django.contrib.auth.models import User
from newapp.models import Customer, Product, OrderItem, Order


class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)


class SignUpForm(LoginForm):
    confirm_password = forms.CharField(max_length=65, widget=forms.PasswordInput)
    name = forms.CharField(max_length=200, required=False)
    email = forms.EmailField(max_length=200, required=False)

    def clean(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('confirm_password')
        username = self.cleaned_data.get('username')
        # email = self.cleaned_data.get('email')

        if password and password != password2:
            raise forms.ValidationError("The two password fields must match.")

        if User.objects.filter(username__exact=username).first() is not None:
            raise forms.ValidationError("Username existed")

        # if Customer.objects.filter(email__exact=email).first() is not None:
        #     raise forms.ValidationError("Email has been used")
        return self.cleaned_data


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def clean(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Negative price")


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ['user']


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'

