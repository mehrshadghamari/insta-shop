from rest_framework import serializers

from apps.shop.models import ImageModel
from apps.shop.models import Post
from apps.shop.models import Product
from apps.shop.models import ProductOptionType
from apps.shop.models import ProductVariant


class ImageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = "__all__"


class PostListSerializer(serializers.ModelSerializer):
    all_image = ImageModelSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "all_image",
            "insta_url",
            "name",
            "description",
            "created_at",
            "updated_at",
        )


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "option_value",
            "price",
            "discount",
            "final_price",
        )


class ProductOptionTypeSerializer(serializers.ModelSerializer):
    prefetched_product_variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = ProductOptionType
        fields = (
            "id",
            "name",
            "prefetched_product_variants",
        )


class ProductSerializer(serializers.ModelSerializer):
    prefetched_option_types = ProductOptionTypeSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "prefetched_option_types",
        )


class PostDetailSerializer(serializers.ModelSerializer):
    prefetched_products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "name",
            "description",
            "prefetched_products",
        )
