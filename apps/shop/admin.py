# Register your models here.
from django.contrib import admin

from apps.shop.models import ImageModel,Product,ProductOptionType,ProductVariant

admin.site.register(Product)
admin.site.register(ImageModel)
admin.site.register(ProductOptionType)
admin.site.register(ProductVariant)
