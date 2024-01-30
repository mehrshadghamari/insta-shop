import uuid
from datetime import datetime
from io import BytesIO

import requests
from django.core.files import File
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.shop.models import ImageModel
from apps.shop.models import Product,ProductOptionType,ProductVariant,Post
from helpers.functions import extract_shortcode
from helpers.functions import fetch_instagram_data
from helpers.functions import generate_unique_filename


class GetFromInsta(APIView):
    def post(self, request):
        shop = self.request.shop

        if not shop:
            return Response({"error": "shop ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        post_url = request.data.get("post_url")
        shortcode = extract_shortcode(post_url)

        if not shortcode:
            return Response({"error": "shortcode parameter is missing"}, status=status.HTTP_400_BAD_REQUEST)

        data = fetch_instagram_data(shortcode)

        if data is None:
            return Response({"error": "Failed to fetch Instagram data"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        images = [image["image_versions2"]["candidates"][3]["url"] for image in data.get("carousel_media", [])]
        caption = data.get("caption", {}).get("text", "")
        location = data.get("location", {}).get("name", "")
        like_count = data.get("like_count", None)

        # Extracting user information
        user_info = data.get("user", {})
        username = user_info.get("username", "")
        profile_pic_url = user_info.get("profile_pic_url", "")

        formatted_response = {
            "user_info": {
                "username": username,
                "profile_pic_url": profile_pic_url,
            },
            "caption": caption,
            "location": location,
            "like_count": like_count,
            "images": images,
        }

        if not images:
            return Response({"error": "No images found in the Instagram post"}, status=status.HTTP_404_NOT_FOUND)

        ############################
        # use chatgpt for create product>>>
        #  dummy data
        variants=[{
            'name' : 'pirahan tak' ,
            'price' : 1500 ,
            'options':{
                'colors' : ['abi','ghermz','sabz'] ,
                'sizes' : ['L','XL','XXL'],
                }
            
            },
            {
            'name' : 'pirahan o shalvar' ,
            'price' : 2500 ,
            'options':{
                'colors' : ['abi o ghermez','ghermz meshki','sabz o ghermez'] ,
                'sizes' : ['L 32','XL 36','XXL 38'],
                }
            },
            {
            'name' : 'shalvar' ,
            'price' : 1800 ,
            'options':{
                'colors' : ['abi','meshki'],
                'sizes' : ['32','36','38']
                }
            },
            ]

        
        with transaction.atomic():
            post_obj = Post.objects.create(shop=shop, insta_url=post_url, name=f"From Instagram - {username}", description=caption)

            # Collect all products and option types first
            all_products = [Product(post=post_obj, name=variant["name"]) for variant in variants]
            Product.objects.bulk_create(all_products)

            all_option_types = []
            all_variants = []

            for variant, product_obj in zip(variants, all_products):
                for option, option_values in variant["options"].items():
                    option_type_obj = ProductOptionType(product=product_obj, name=option)
                    all_option_types.append(option_type_obj)
                    
            # Bulk create all option types
            ProductOptionType.objects.bulk_create(all_option_types)

            # Map created option types to their names and products for easy lookup
            option_types_mapping = {(opt.product_id, opt.name): opt for opt in all_option_types}

            for variant, product_obj in zip(variants, all_products):
                for option, option_values in variant["options"].items():
                    option_type_obj = option_types_mapping[(product_obj.id, option)]
                    variants_to_create = [
                        ProductVariant(option_type=option_type_obj, option_value=value, price=variant["price"]) 
                        for value in option_values
                    ]
                    all_variants.extend(variants_to_create)

            # Bulk create all variants at once
            ProductVariant.objects.bulk_create(all_variants)


            self.save_images_to_database(images, username, post_obj)

        return Response(data, status=status.HTTP_200_OK)


    def save_images_to_database(self, images, username, post):
        for image_url in images:
            try:
                response = requests.get(image_url, timeout=15)  # timeout in seconds

                if response.status_code == 200:
                    image_data = BytesIO(response.content)
                    unique_filename = generate_unique_filename(username)

                    # Create a new ImageModel instance
                    post_image = ImageModel(content_object=post)
                    post_image.image.save(unique_filename, File(image_data))
                    post_image.save()
                else:
                    # Handle non-successful status codes
                    pass  # Add logging or error handling as needed
            except requests.RequestException as e:
                # Handle exceptions
                pass  # Add logging or error handling as needed









# normal code 

# with transaction.atomic():
#     post_obj = Post.objects.create(shop=shop, insta_url=post_url, name=f"From Instagram - {username}", description=caption)

#     for variant in variants:
#         product_obj = Product.objects.create(post=post_obj, name=variant["name"])

#         for option, option_values in variant["options"].items():
#             product_option_type_obj = ProductOptionType.objects.create(product=product_obj, name=option)
            
#             # Create ProductVariant instances
#             variants_to_create = [
#                 ProductVariant(option_type=product_option_type_obj, option_value=value, price=variant["price"]) 
#                 for value in option_values
#             ]
#             ProductVariant.objects.bulk_create(variants_to_create)
            


# better

# with transaction.atomic():
#     post_obj = Post.objects.create(shop=shop, insta_url=post_url, name=f"From Instagram - {username}", description=caption)

#     # Collect all products and option types first
#     all_products = [Product(post=post_obj, name=variant["name"]) for variant in variants]
#     Product.objects.bulk_create(all_products)

#     all_option_types = []
#     all_variants = []

#     for variant, product_obj in zip(variants, all_products):
#         for option, option_values in variant["options"].items():
#             option_type_obj = ProductOptionType(product=product_obj, name=option)
#             all_option_types.append(option_type_obj)
            
#     # Bulk create all option types
#     ProductOptionType.objects.bulk_create(all_option_types)

#     # Map created option types to their names and products for easy lookup
#     option_types_mapping = {(opt.product_id, opt.name): opt for opt in all_option_types}

#     for variant, product_obj in zip(variants, all_products):
#         for option, option_values in variant["options"].items():
#             option_type_obj = option_types_mapping[(product_obj.id, option)]
#             variants_to_create = [
#                 ProductVariant(option_type=option_type_obj, option_value=value, price=variant["price"]) 
#                 for value in option_values
#             ]
#             all_variants.extend(variants_to_create)

#     # Bulk create all variants at once
#     ProductVariant.objects.bulk_create(all_variants)