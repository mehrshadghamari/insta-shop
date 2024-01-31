# Register your models here.
from django.contrib import admin

from apps.shop.models import ImageModel
from apps.shop.models import Post
from apps.shop.models import Product
from apps.shop.models import ProductOptionType
from apps.shop.models import ProductVariant

admin.site.register(Post)
admin.site.register(Product)
admin.site.register(ImageModel)
admin.site.register(ProductOptionType)
admin.site.register(ProductVariant)
