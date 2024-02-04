import math

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.shop.models import Post
from apps.shop.models import Product
from apps.shop.models import ProductOptionType
from apps.shop.models import ProductVariant
from apps.shop.serializers import PostDetailSerializer
from apps.shop.serializers import PostListSerializer
from apps.shop.tasks import process_instagram_post
from helpers.caches import cache_handler
from helpers.instagram_APIs import InstagramFetchStrategyFactory
from helpers.utils import extract_shortcode

# Configure logging
# logger = logging.getLogger(__name__)


class GetFromInsta(APIView):
    def post(self, request):
        shop = request.shop
        if not shop:
            return Response({"error": "Shop ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        post_url = request.data.get("post_url")
        shortcode = extract_shortcode(post_url)
        if not shortcode:
            return Response({"error": "Shortcode parameter is missing"}, status=status.HTTP_400_BAD_REQUEST)

        instagram_api = InstagramFetchStrategyFactory()
        data = instagram_api.fetch_data(shortcode)
        if data is None:
            return Response({"error": "Failed to fetch Instagram data"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Offload heavy processing to Celery task
        process_instagram_post.delay(shop.id, post_url, data)

        # Immediate response to client
        return Response({"message": "Instagram data is being processed"}, status=status.HTTP_202_ACCEPTED)


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
            query = Post.objects.filter(shop=shop_id).prefetch_related("images")
            serializer = PostListSerializer(query, many=True, context={"request": request})
            data = serializer.data
            cache_handler.set(cache_key, data, cache_time)

        page_count = math.ceil(len(data) / page_size)
        paginate_data = data[page_size * (page_number - 1) : page_size * (page_number)]

        res = {
            "current_page": page_number,
            "page_count": page_count,
            "posts": paginate_data,
        }

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
