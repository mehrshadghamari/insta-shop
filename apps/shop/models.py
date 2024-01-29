from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models

from apps.panel.models import Shop
from apps.panel.models import TimeStampedModel


class Product(TimeStampedModel):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="products")

    name = models.CharField(max_length=64)
    description = models.TextField(null=True, blank=True)

    @property
    def options(self):
        return self.options.all()

    def __str__(self):
        return f"id : {self.id} -- name : {self.name} "


class ProductOptionType(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, related_name="options")
    name = models.CharField(max_length=127, null=True, blank=True)
    no_option = models.BooleanField(default=False)

    @property
    def product_variant(self):
        return self.values.all()


class ProductVariant(TimeStampedModel):
    option = models.ForeignKey(ProductOptionType, on_delete=models.CASCADE, related_name="values")
    option_value = models.CharField(max_length=127, null=True, blank=True)
    price = models.FloatField()
    discount = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(99), MinValueValidator(0)])

    @property
    def final_price(self):
        if self.discount == 0:
            final_price = self.price
        else:
            final_price = float(self.price - (self.price * self.discount / 100))
        return final_price
