from celery import shared_task
from django.db import transaction
import requests
from io import BytesIO
from .models import Shop, Post, Product, ProductOptionType, ProductVariant, ImageModel
from  helpers.utils import extract_shortcode, generate_unique_filename, extract_images, get_dummy_variants


# @shared_task
# def process_instagram_post(shop_id, post_url, shortcode):
#     try:
#         instagram_API = InstagramFetchStrategyFactory()
#         data = instagram_API.fetch_data(shortcode)
#         if not data:
#             print("Failed to fetch Instagram data")
#             return

#         with transaction.atomic():
#             # Create the post object
#             user_info = data.get("user", {})
#             shop = Shop.objects.get(id=shop_id)
#             post = Post.objects.create(
#                 shop=shop,
#                 insta_url=post_url,
#                 name=f"From Instagram - {user_info.get('username', '')}",
#                 description=data.get("caption", {}).get("text", "")
#             )

#             # Extract images and save them
#             images = extract_images(data)  # Make sure this function returns the image URLs correctly
#             for i, image_url in enumerate(images):
#                 is_main = i == 0
#                 response = requests.get(image_url, timeout=15)
#                 if response.status_code == 200:
#                     image_data = BytesIO(response.content)
#                     filename = generate_unique_filename(user_info.get('username', 'unknown'))
#                     post_image = ImageModel(post=post, is_main=is_main)
#                     post_image.image.save(filename, File(image_data))

#             # Process and save product variants
#             variants = get_dummy_variants()  # This should be adjusted to extract variants from `data`
#             create_products_and_variants(post, variants)

#     except Exception as e:
#         # It's important to log errors in tasks for debugging
#         print(f"Error processing Instagram post: {e}")


# def create_products_and_variants(post, variants):
#     for variant in variants:
#         product = Product.objects.create(
#             post=post, 
#             name=variant["name"], 
#             price=variant["price"]
#         )
        
#         for option_name, option_values in variant["options"].items():
#             option_type = ProductOptionType.objects.create(
#                 product=product, 
#                 name=option_name
#             )
            
#             for value in option_values:
#                 ProductVariant.objects.create(
#                     option_type=option_type, 
#                     option_value=value
#                 )




def process_instagram_post(shop_id, post_url, instagram_data):
    try:
        data = json.loads(instagram_data)  # Assuming instagram_data is a JSON string
        images = extract_images(data)  # Ensure this works with your data structure

        with transaction.atomic():
            user_info = data.get("user", {})
            shop = Shop.objects.get(id=shop_id)
            post = Post.objects.create(
                shop=shop,
                insta_url=post_url,
                name=f"From Instagram - {user_info.get('username', '')}",
                description=data.get("caption", {}).get("text", "")
            )

            for i, image_url in enumerate(images):
                is_main = i == 0
                response = requests.get(image_url)
                if response.status_code == 200:
                    image_data = BytesIO(response.content)
                    filename = generate_unique_filename(user_info.get('username', 'unknown'))
                    post_image = ImageModel(post=post, is_main=is_main)
                    post_image.image.save(filename, File(image_data))

            # Add your logic for creating products, variants, and option types here
            # Similar to how it was done in your previous implementation
            
    except Exception as e:
        print(f"Error processing Instagram data for shop {shop_id}: {e}")

