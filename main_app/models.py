from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.


class CustomUser(AbstractUser):
    wallet = models.FloatField(default=10000.0)

    def __str__(self):
        return self.username


class Product(models.Model):
    name_of_product = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    price = models.FloatField()
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['name_of_product', ]

    def __str__(self):
        return self.name_of_product


class Purchase(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    time_of_purchase = models.DateTimeField(auto_now_add=True)
    total_sum = models.FloatField(default=0)

    class Meta:
        ordering = ['-time_of_purchase', ]


class Returns(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    time_of_return = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["time_of_return"]
