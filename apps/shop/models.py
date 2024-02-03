from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models

from apps.panel.models import Shop
from apps.panel.models import TimeStampedModel


class Post(TimeStampedModel):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="products")
    insta_url = models.URLField()

    name = models.CharField(max_length=64)
    description = models.TextField(null=True, blank=True)

    images = GenericRelation(
        to="shop.ImageModel",
        content_type_field="content_type",
        object_id_field="object_id",
        related_query_name="product_image",
    )

    @property
    def all_images(self):
        return self.images.all()

    @property
    def main_image(self):
        obj = self.images.filter(is_main=True).first()
        if not obj:
            obj = self.images.first()
        return obj

    def __str__(self):
        return f"id : {self.id} -- name : {self.name} "


class Product(TimeStampedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=127)
    price = models.FloatField()
    discount = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(99), MinValueValidator(0)])

    @property
    def final_price(self):
        if self.discount == 0:
            final_price = self.price
        else:
            final_price = float(self.price - (self.price * self.discount / 100))
        return final_price

    @property
    def options(self):
        return self.option_types.all()

    def __str__(self):
        return f"id : {self.id} -- name : {self.name} "


class ProductOptionType(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="option_types")
    name = models.CharField(max_length=127)  # e.g., "color", "size"

    @property
    def option_values(self):
        return self.values.all()

    def __str__(self):
        return self.name


class ProductVariant(TimeStampedModel):
    option_type = models.ForeignKey(ProductOptionType, on_delete=models.CASCADE, related_name="values")
    option_value = models.CharField(max_length=127)  # e.g., "red", "blue", "L", "XL"

    def __str__(self):
        return self.option_value


class ImageModel(TimeStampedModel):
    image = models.ImageField()
    is_main = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=127, default=None, null=True, blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")
