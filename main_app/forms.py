from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.utils import timezone
from datetime import timedelta
from main_app.exceptions import ValidationError
from main_app.models import CustomUser, Product, Purchase, Returns
from online_shop.settings import ALLOWED_TIME_TO_RETURN


class UserCreateForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username']


class ProductCreateForm(ModelForm):
    class Meta:
        model = Product
        fields = ['name_of_product', 'description', 'price', 'quantity']

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise ValidationError('The price of product must be more then 0!')
        return price

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise ValidationError('The quantity of product must be more then 0!')
        return quantity


class PurchaseCreateForm(ModelForm):
    class Meta:
        model = Purchase
        fields = ['quantity', ]

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        if 'pk' in kwargs:
            self.product_id = kwargs.pop('pk')
        return super().__init__(*args, **kwargs)

    def clean(self):
        cleand_data = super().clean()
        if not cleand_data.get('quantity'):
            self.add_error(None, "Error")
            messages.error(self.request, 'You must order at least 1 unit!')
        try:
            product = Product.objects.get(pk=self.product_id)
            self.product = product
            if cleand_data.get('quantity') > product.quantity:
                self.add_error(None, 'Error')
                messages.error(self.request, 'You have ordered more than we have in stock!')
            if self.request.user.wallet < cleand_data.get('quantity') * product.price:
                self.add_error(None, 'Error')
                messages.error(self.request, 'You do not have enough money in your account!')
        except Product.DoesNotExist:
            self.add_error(None, 'Error')
            messages.error(self.request, 'This product does not exist!')


class ReturnsCreateForm(ModelForm):
    class Meta:
        model = Returns
        fields = []

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        if 'pk' in kwargs:
            self.purchase_id = kwargs.pop('pk')
        return super().__init__(*args, **kwargs)

    def clean(self):
        cleand_data = super().clean()
        try:
            purchase = Purchase.objects.get(pk=self.purchase_id)
            self.purchase = purchase
            if purchase.time_of_purchase + timedelta(seconds=ALLOWED_TIME_TO_RETURN) < timezone.now():
                self.add_error(None, 'Error')
                messages.error(self.request, 'Time to return purchase has passed!')
            if Returns.objects.filter(purchase_id=purchase.id).exists():
                self.add_error(None, 'Error')
                messages.error(self.request, 'You have already applied for a return!')
        except Purchase.DoesNotExist:
            self.add_error(None, 'Error')
            messages.error(self.request, 'This purchase does not exist!')
