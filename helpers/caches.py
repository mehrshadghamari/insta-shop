from django.core.cache import cache

from apps.shop.models import Post


def clear_related_post_cache(instance):
    post_ids = set()
    shop_ids = set()

    if hasattr(instance, "post_id"):
        post_ids.add(instance.post_id)
        shop_id = getattr(instance, "shop_id", None) or getattr(instance.post, "shop_id", None)
        if shop_id:
            shop_ids.add(shop_id)

    elif hasattr(instance, "content_object"):
        content_object = instance.content_object
        if isinstance(content_object, Post):
            post_ids.add(content_object.id)
            shop_ids.add(content_object.shop_id)

    elif hasattr(instance, "product"):
        post_id = getattr(instance.product, "post_id", None)
        shop_id = getattr(instance.product.post, "shop_id", None)
        post_ids.add(post_id)
        shop_ids.add(shop_id)

    elif hasattr(instance, "option_type") and hasattr(instance.option_type, "product"):
        product = instance.option_type.product
        if hasattr(product, "post"):
            post = product.post
            post_ids.add(post.id)
            if hasattr(post, "shop_id"):
                shop_ids.add(post.shop_id)

    for post_id in post_ids:
        cache.delete(f"post_detail_{post_id}")
    for shop_id in shop_ids:
        cache.delete(f"post_list_{shop_id}")
