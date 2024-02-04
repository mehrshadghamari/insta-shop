from io import BytesIO

import requests
from celery import shared_task
from django.core.files import File
from django.db import transaction

from helpers.utils import generate_unique_filename

from .models import ImageModel
from .models import Post
from .models import Product
from .models import ProductOptionType
from .models import ProductVariant


# Helper functions
def create_post(shop_id, post_url, data):
    user_info = data.get("user", {})
    post = Post.objects.create(
        shop_id=shop_id,
        insta_url=post_url,
        name=f"From Instagram - {user_info.get('username', '')}",
        description=data.get("caption", {}).get("text", ""),
    )
    return post


def create_products_and_variants(post, variants):
    all_products = [Product(post=post, name=variant["name"], price=variant["price"]) for variant in variants]
    Product.objects.bulk_create(all_products)

    all_option_types = []
    all_variants = []
    for variant, product_obj in zip(variants, all_products):
        for option, option_values in variant["options"].items():
            option_type_obj = ProductOptionType(product=product_obj, name=option)
            all_option_types.append(option_type_obj)

    ProductOptionType.objects.bulk_create(all_option_types)
    option_types_mapping = {opt.name: opt for opt in all_option_types}

    for variant, product_obj in zip(variants, all_products):
        for option, option_values in variant["options"].items():
            option_type_obj = option_types_mapping[option]
            for value in option_values:
                ProductVariant.objects.create(option_type=option_type_obj, option_value=value)


def save_images_to_database(post, images):
    for i, image_url in enumerate(images):
        is_main = i == 0
        response = requests.get(image_url, timeout=15)
        if response.status_code == 200:
            image_data = BytesIO(response.content)
            filename = generate_unique_filename(post.name)
            post_image = ImageModel(content_object=post, is_main=is_main)
            post_image.image.save(filename, File(image_data))
            post_image.save()


def format_response(data, images):
    user_info = data.get("user", {})
    return {
        "user_info": {
            "username": user_info.get("username", ""),
            "profile_pic_url": user_info.get("profile_pic_url", ""),
        },
        "caption": data.get("caption", {}).get("text", ""),
        # "location": data.get("location", {}).get("name", ""),
        # "like_count": data.get("like_count", None),
        "images": images,
    }


def get_dummy_variants():
    # Replace this method with chat gpt logic to fetch or create variants
    return [
        {
            "name": "pirahan tak",
            "price": 1500,
            "options": {
                "colors": ["abi", "ghermz", "sabz"],
                "sizes": ["L", "XL", "XXL"],
            },
        },
        {
            "name": "pirahan o shalvar",
            "price": 2500,
            "options": {
                "colors": ["abi o ghermez", "ghermz meshki", "sabz o ghermez"],
                "sizes": ["L 32", "XL 36", "XXL 38"],
            },
        },
        {
            "name": "shalvar",
            "price": 1800,
            "options": {
                "colors": ["abi", "meshki"],
                "sizes": ["32", "36", "38"],
            },
        },
    ]


# Main task
@shared_task
def process_instagram_post(shop_id, post_url, data):
    try:
        images = [image["image_versions2"]["candidates"][3]["url"] for image in data.get("carousel_media", [])]
        variants = get_dummy_variants()

        with transaction.atomic():
            post_obj = create_post(shop_id, post_url, data)
            create_products_and_variants(post_obj, variants)
            save_images_to_database(post_obj, images)

    except Exception as e:
        print(f"Error processing Instagram data for shop {shop_id}: {e}")
