import logging
from io import BytesIO

import requests
from django.core.cache import cache
from django.core.files import File
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.shop.models import ImageModel
from apps.shop.models import Post
from apps.shop.models import Product
from apps.shop.models import ProductOptionType
from apps.shop.models import ProductVariant
from apps.shop.serializers import PostDetailSerializer
from apps.shop.serializers import PostListSerializer
from helpers.APIs import fetch_instagram_data
from helpers.utils import extract_shortcode
from helpers.utils import generate_unique_filename

# Configure logging
# logger = logging.getLogger(__name__)


class GetFromInsta(APIView):
    def post(self, request):
        shop = self.request.shop
        if not shop:
            return Response({"error": "Shop ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        post_url = request.data.get("post_url")
        shortcode = extract_shortcode(post_url)
        if not shortcode:
            return Response({"error": "Shortcode parameter is missing"}, status=status.HTTP_400_BAD_REQUEST)

        data = fetch_instagram_data(shortcode)
        if data is None:
            return Response({"error": "Failed to fetch Instagram data"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        images = self.extract_images(data)
        if not images:
            return Response({"error": "No images found in the Instagram post"}, status=status.HTTP_404_NOT_FOUND)

        formatted_response = self.format_response(data, images)

        variants = self.get_dummy_variants()  # Replace with actual logic to get variants

        with transaction.atomic():
            post_obj = self.create_post(shop, post_url, data)
            self.create_products_and_variants(post_obj, variants)
            self.save_images_to_database(images, post_obj)

        return Response(formatted_response, status=status.HTTP_200_OK)

    def extract_images(self, data):
        return [image["image_versions2"]["candidates"][3]["url"] for image in data.get("carousel_media", [])]

    def format_response(self, data, images):
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

    def create_post(self, shop, post_url, data):
        user_info = data.get("user", {})
        return Post.objects.create(
            shop=shop,
            insta_url=post_url,
            name=f"From Instagram - {user_info.get('username', '')}",
            description=data.get("caption", {}).get("text", ""),
        )

    def create_products_and_variants(self, post_obj, variants):
        all_products = [Product(post=post_obj, name=variant["name"]) for variant in variants]
        Product.objects.bulk_create(all_products)

        all_option_types = []
        all_variants = []
        for variant, product_obj in zip(variants, all_products):
            for option, option_values in variant["options"].items():  # noqa:B007
                option_type_obj = ProductOptionType(
                    product=product_obj,
                    name=option,
                )
                all_option_types.append(option_type_obj)

        ProductOptionType.objects.bulk_create(all_option_types)
        option_types_mapping = {(opt.product_id, opt.name): opt for opt in all_option_types}

        for variant, product_obj in zip(variants, all_products):
            for option, option_values in variant["options"].items():
                option_type_obj = option_types_mapping[(product_obj.id, option)]
                variants_to_create = [
                    ProductVariant(option_type=option_type_obj, option_value=value, price=variant["price"])
                    for value in option_values
                ]
                all_variants.extend(variants_to_create)

        ProductVariant.objects.bulk_create(all_variants)

    def save_images_to_database(self, images, post):
        for i, image_url in enumerate(images):
            is_main = True if i == 0 else False
            try:
                response = requests.get(image_url, timeout=15)  # timeout in seconds
                if response.status_code == 200:
                    image_data = BytesIO(response.content)
                    unique_filename = generate_unique_filename(post.name)
                    post_image = ImageModel(content_object=post, is_main=is_main)
                    post_image.image.save(unique_filename, File(image_data))
                    post_image.save()
            except requests.RequestException as e:
                pass
                # logger.error(f"Failed to download image: {image_url}, Error: {e}")  # noqa : G004

    def get_dummy_variants(self):
        # Replace this method with actual logic to fetch or create variants
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


class PostList(APIView):
    def get(self, request):
        shop_id = request.shop.id
        cache_key = f"post_list_{shop_id}"
        cache_time = 60 * 15  # Cache for 15 minutes

        # Try to get data from cache
        data = cache.get(cache_key)
        if not data:
            query = Post.objects.filter(shop=shop_id).prefetch_related("images")
            serializer = PostListSerializer(query, many=True, context={"request": request})
            data = serializer.data
            cache.set(cache_key, data, cache_time)

        return Response(data, status=status.HTTP_200_OK)


class PostDetail(APIView):
    def get(self, request, pk):
        cache_key = f"post_detail_{pk}"
        cache_time = 60 * 15  # cache for 15 minutes
        data = cache.get(cache_key)

        if not data:
            shop_id = request.shop.id

            product_variant_prefetch = Prefetch(
                "values",
                queryset=ProductVariant.objects.all(),
                to_attr="variants",
            )

            product_option_type_prefetch = Prefetch(
                "option_types",
                queryset=ProductOptionType.objects.prefetch_related(product_variant_prefetch),
                to_attr="product_options",
            )

            product_prefetch = Prefetch(
                "products",
                queryset=Product.objects.filter(post=pk).prefetch_related(product_option_type_prefetch),
                to_attr="all_products",
            )

            post = get_object_or_404(Post.objects.prefetch_related("images", product_prefetch), id=pk, shop=shop_id)

            serializer = PostDetailSerializer(post, context={"request": request})
            data = serializer.data
            cache.set(cache_key, data, cache_time)
        return Response(data, status=status.HTTP_200_OK)


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
