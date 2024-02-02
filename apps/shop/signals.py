from django.contrib.contenttypes.fields import ContentType
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.shop.models import ImageModel
from apps.shop.models import Post
from apps.shop.models import Product
from apps.shop.models import ProductOptionType
from apps.shop.models import ProductVariant
from helpers.caches import clear_related_post_cache


@receiver(post_save, sender=Post)
@receiver(post_delete, sender=Post)
@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
@receiver(post_save, sender=ProductOptionType)
@receiver(post_delete, sender=ProductOptionType)
@receiver(post_save, sender=ProductVariant)
@receiver(post_delete, sender=ProductVariant)
@receiver(post_save, sender=ImageModel)
@receiver(post_delete, sender=ImageModel)
def clear_cache(sender, instance, **kwargs):
    clear_related_post_cache(instance)
