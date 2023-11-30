from django import forms
from django.contrib.auth.models import User
from django.db.models import Model

from newapp.models import Customer, Product


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

        if password and password != password2:
            raise forms.ValidationError("The two password fields must match.")

        if User.objects.filter(username__exact=username).first() is not None:
            raise forms.ValidationError("Username existed")

        return self.cleaned_data


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
