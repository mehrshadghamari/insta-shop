from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models

from apps.panel.models import Shop
from apps.panel.models import TimeStampedModel


class Product(TimeStampedModel):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="products")

    name = models.CharField(max_length=64)
    description = models.TextField(null=True, blank=True)

    images = GenericRelation(
        to="shop.ImageModel",
        content_type_field="content_type",
        object_id_field="object_id",
        related_query_name="product_image",
    )

    @property
    def options(self):
        return self.options.all()

    @property
    def all_image(self):
        return self.images.all()

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


class ImageModel(TimeStampedModel):
    image = models.ImageField()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")
