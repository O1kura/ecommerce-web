import os
from pathlib import Path

from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver

from newproj import settings


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)

    class Meta:
        db_table = 'customer'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField()
    digital = models.BooleanField(default=False, null=True, blank=False)
    image = models.ImageField(null=True, blank=True, )
    # is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'product'

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except ValueError:
            url = ''
        return url


@receiver(models.signals.pre_delete, sender=Product)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    img = instance.image
    old_file = instance.imageURL
    path = Path(os.path.join(settings.MEDIA_ROOT, img.name))

    if old_file != '':
        if os.path.isfile(path):
            os.remove(path)


@receiver(models.signals.pre_save, sender=Product)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.id:
        return False

    product = Product.objects.get(id=instance.id)
    img = product.image
    old_file = product.imageURL
    path = Path(os.path.join(settings.MEDIA_ROOT, img.name))

    if old_file == '':
        return False

    new_file = instance.imageURL
    if not old_file == new_file:
        os.remove(path)


@receiver(models.signals.pre_save, sender=User)
def auto_change_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.id:
        return False

    user = User.objects.get(id=instance.id)
    email = user.email

    if not email == instance.email:
        customer = Customer.objects.get(user=user)
        customer.email = instance.email
        customer.save()


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=True)
    transaction_id = models.CharField(max_length=200, null=True)

    class Meta:
        db_table = 'order'

    @property
    def shipping(self):
        orderItems = self.orderitem_set.all()

        for item in orderItems:
            if not item.product.digital:
                return True
        return False

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    def __str__(self):
        return str(self.id)


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_item'

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

    def __str__(self):
        return f'order: {self.order.id} {self.product.name}'


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shipping_address'

    def __str__(self):
        return f'order: {self.order.id} {self.address}'
