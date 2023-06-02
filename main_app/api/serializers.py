from datetime import timedelta
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from main_app.models import CustomUser, Product, Purchase, Returns
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from online_shop.settings import ALLOWED_TIME_TO_RETURN
from django.contrib.auth import password_validation


class CustomUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True,
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'password', 'wallet')

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_username(self, value):
        users = CustomUser.objects.filter(username__iexact=value)
        if users.exists():
            raise ValidationError("User with this name already exists")
        return value

    def validate_password(self, value):
        if ' ' in value:
            raise ValidationError("Password must not contain whitespaces")
        password_validation.validate_password(value, self.instance)
        return value

    def validate_wallet(self, value):
        if value <= 0:
            raise ValidationError('Summ of money on your`s wallet must be more then 0')
        if value > 10000:
            raise ValidationError('Summ of money on your`s wallet should`t be more then 10000')
        return value


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'name_of_product', 'description', 'price', 'quantity']

    def validate_name_of_product(self, value):
        if not value:
            raise ValidationError('You must write the name of product')
        if len(value) < 3:
            raise ValidationError('The name of product can`t be less then 3 symbols')
        exists_product = Product.objects.filter(name_of_product__iexact=value)
        if exists_product.exists():
            raise ValidationError("Product with this name already exist")

        return value

    def validate_description(self, value):
        if not value:
            raise ValidationError('You must write description of product')
        if len(value) < 10:
            raise ValidationError('Description of product can`t be less then 10 symbols')
        return value

    def validate_price(self, value):
        if value <= 0:
            raise ValidationError('Price of product must be more then 0')
        return value

    def validate_quantity(self, value):
        if value <= 0:
            raise ValidationError('Quantity of the product must be more then 0')
        return value


class PurchaseSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), required=False)
    time_of_purchase = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Purchase
        fields = ['id', 'user', 'product', 'quantity', 'time_of_purchase', 'total_sum']

    def validate(self, data):
        if data['quantity'] < 1:
            raise ValidationError('You must order at least 1 unit!')
        if data['quantity'] > data['product'].quantity:
            raise ValidationError('You have ordered more than we have in stock')
        if self.context['user'].wallet < data['quantity'] * data['product'].price:
            raise ValidationError('You do not have enough money in your account')
        return data

    def create(self, validated_data):
        user = self.context['user']
        validated_data['user'] = user
        total_sum = validated_data['quantity'] * validated_data['product'].price
        validated_data['total_sum'] = total_sum
        purchase = Purchase.objects.create(**validated_data)
        return purchase

    def get_user(self):
        return self.context['request']


class ReturnsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Returns
        fields = ['id', 'purchase', 'time_of_return']

    def validate(self, data):
        if data['purchase'].time_of_purchase + timedelta(seconds=ALLOWED_TIME_TO_RETURN) < timezone.now():
            raise ValidationError('Time to return purchase has passed!')
        if Returns.objects.filter(purchase_id=data['purchase'].id).exists():
            raise ValidationError('You have already applied for a return!')
        return data

