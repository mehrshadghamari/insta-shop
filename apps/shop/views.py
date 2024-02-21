import logging
import math
import re
from io import BytesIO

import requests
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
from apps.shop.serializers import PostUpdateSerializer
from apps.shop.serializers import ProductCreateSerializer
from apps.shop.serializers import ProductUpdateSerializer
from helpers.caches import cache_handler
from helpers.chat_gpt.gpt_api import generate_data
from helpers.instagram_APIs import InstagramFetchStrategyFactory
from helpers.utils import clean_caption
from helpers.utils import extract_shortcode
from helpers.utils import generate_unique_filename

# Configure logging
logger = logging.getLogger(__name__)


class GetFromInsta(APIView):
    def post(self, request):
        shop = self.request.shop
        if not shop:
            logger.error("Shop ID is missing from the request.")
            return Response({"error": "Shop ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        post_url = request.data.get("post_url")
        shortcode = extract_shortcode(post_url)
        if not shortcode:
            logger.error("Shortcode extraction failed from the provided URL.")
            return Response({"error": "Shortcode parameter is missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instagram_api = InstagramFetchStrategyFactory()
            data = instagram_api.fetch_data(shortcode)
        except Exception:
            logger.error(f"Failed to fetch Instagram data for shortcode {shortcode}: {e}")
            return Response({"error": "Failed to fetch Instagram data"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        images = self.extract_images(data)
        if not images:
            logger.error(f"No images found in the Instagram post for shortcode {shortcode}.")
            return Response({"error": "No images found in the Instagram post"}, status=status.HTTP_404_NOT_FOUND)

        # Fetch caption and clean it
        raw_caption = data.get("caption", {}).get("text", "")
        cleaned_caption = clean_caption(raw_caption)

        gpt_response, gpt_status = generate_data(caption=cleaned_caption)
        if gpt_status != status.HTTP_200_OK:
            return Response(
                {"error": gpt_response["error"], "gpt_status": gpt_status, "type": "GPT"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        variants = gpt_response  # Assuming gpt_response is the list of dictionaries with product data

        # Process and save the fetched data
        try:
            with transaction.atomic():
                post_obj = self.create_post(shop, post_url, data)
                self.create_products_and_variants(post_obj, variants)
                self.save_images_to_database(images, post_obj)
        except Exception as e:
            logger.error(f"Failed to process and save fetched data: {e}")
            return Response(
                {"error": "Failed to process Instagram post data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        logger.info(f"Instagram post data successfully processed and saved for shortcode {shortcode}.")
        return Response({"msg": "Added successfully"}, status=status.HTTP_201_CREATED)

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
        all_products = [Product(post=post_obj, name=variant["name"], price=variant["price"]) for variant in variants]
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
                    ProductVariant(option_type=option_type_obj, option_value=value) for value in option_values
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


class PostList(APIView):
    def get(self, request):
        page_number = int(self.request.query_params.get("page", 1))  # default page=1
        page_size = int(self.request.query_params.get("page_size", 2))  # default page size=20
        shop_id = request.shop.id
        cache_key = f"post_list_{shop_id}"
        cache_time = 60 * 15  # Cache for 15 minutes

        # Try to get data from cache
        data = cache_handler.get(cache_key)
        if not data:
            query = Post.objects.filter(shop=shop_id).prefetch_related("images").order_by("-updated_at")
            serializer = PostListSerializer(query, many=True, context={"request": request})
            data = serializer.data
            cache_handler.set(cache_key, data, cache_time)

        page_count = math.ceil(len(data) / page_size)
        paginate_data = data[page_size * (page_number - 1) : page_size * (page_number)]

        res = {"current_page": page_number, "page_count": page_count, "posts": paginate_data}

        return Response(res, status=status.HTTP_200_OK)


class PostDetail(APIView):
    def get(self, request, pk):
        cache_key = f"post_detail_{pk}"
        cache_time = 60 * 15  # cache for 15 minutes
        data = cache_handler.get(cache_key)

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
            cache_handler.set(cache_key, data, cache_time)
        return Response(data, status=status.HTTP_200_OK)


class PostUpdate(APIView):
    def put(self, request):
        shop_id = request.shop.id
        post_id = request.query_params.get("post-id")

        serializer = PostUpdateSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.data
            post = get_object_or_404(Post, id=post_id, shop_id=shop_id)
            post.name = data.get("name", post.name)
            post.description = data.get("description", post.description)
            post.save()

            return Response({"message": "Post updated successfully"}, status=status.HTTP_200_OK)

        else:
            # Return errors if data is invalid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDelete(APIView):
    def delete(self, request):
        shop_id = request.shop.id
        post_id = request.query_params.get("post-id")
        post = get_object_or_404(Post, id=post_id, shop_id=shop_id)
        post.delete()
        return Response({"message": "Post deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class ProductUpdate(APIView):
    def put(self, request):
        shop_id = request.shop.id
        post_id = request.query_params.get("post-id")

        serializer = ProductUpdateSerializer(data=request.data)

        if serializer.is_valid():
            product_data = serializer.validated_data

            post = get_object_or_404(Post, id=post_id, shop_id=shop_id)

            product_id = product_data.get("id")

            product = Product.objects.filter(id=product_id, post=post).first()

            if product:
                product.name = product_data["name"]
                product.price = product_data["price"]
                product.save()
            else:
                return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

            # Delete existing options and recreate
            ProductOptionType.objects.filter(product=product).delete()
            for option_name, option_values in product_data["options"].items():
                option_type = ProductOptionType.objects.create(product=product, name=option_name)
                for value in option_values:
                    ProductVariant.objects.create(option_type=option_type, option_value=value)

            return Response({"message": "Products updated successfully"}, status=status.HTTP_200_OK)

        else:
            # Return errors if data is invalid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductCreate(APIView):
    def post(self, request):
        shop_id = request.shop.id
        post_id = request.query_params.get("post-id")

        serializer = ProductCreateSerializer(data=request.data)

        if serializer.is_valid():
            product_data = serializer.validated_data

            post = get_object_or_404(Post, id=post_id, shop_id=shop_id)

            product = Product.objects.create(
                post=post,
                name=product_data["name"],
                price=product_data["price"],
            )
            # Delete existing options and recreate
            ProductOptionType.objects.filter(product=product).delete()
            for option_name, option_values in product_data["options"].items():
                option_type = ProductOptionType.objects.create(product=product, name=option_name)
                for value in option_values:
                    ProductVariant.objects.create(option_type=option_type, option_value=value)

            return Response({"message": "Product created successfully"}, status=status.HTTP_201_CREATED)

        else:
            # Return errors if data is invalid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDelete(APIView):
    def delete(self, request):
        shop_id = request.shop.id
        product_id = request.query_params.get("product-id")
        product = get_object_or_404(Product, id=product_id, post__shop_id=shop_id)
        product.delete()
        return Response({"message": "product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# with redis cache


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
