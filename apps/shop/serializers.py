from rest_framework import serializers

from apps.shop.models import ImageModel
from apps.shop.models import Post
from apps.shop.models import Product
from apps.shop.models import ProductOptionType
from apps.shop.models import ProductVariant


class ImageModelSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField("get_image_url")

    def get_image_url(self, obj):
        request = self.context.get("request")
        image_url = obj.image.url
        return request.build_absolute_uri(image_url)

    class Meta:
        model = ImageModel
        fields = (
            "id",
            "image",
            "is_main",
            # "alt_text",
        )


class PostListSerializer(serializers.ModelSerializer):
    main_image = ImageModelSerializer(many=False, read_only=True)
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    prices = serializers.ListField()

    def get_created_at(self, obj):
        return int(obj.created_at.timestamp())

    def get_updated_at(self, obj):
        return int(obj.updated_at.timestamp())

    class Meta:
        model = Post
        fields = (
            "id",
            "main_image",
            "insta_url",
            "name",
            "prices",
            "created_at",
            "updated_at",
        )


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "option_value",
        )


class ProductOptionTypeSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = ProductOptionType
        fields = (
            "id",
            "name",
            "variants",
        )


class ProductSerializer(serializers.ModelSerializer):
    product_options = ProductOptionTypeSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "price",
            "discount",
            "final_price",
            "product_options",
        )


class PostDetailSerializer(serializers.ModelSerializer):
    all_products = ProductSerializer(many=True, read_only=True)
    all_images = ImageModelSerializer(many=True, read_only=True)
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return int(obj.created_at.timestamp())

    def get_updated_at(self, obj):
        return int(obj.updated_at.timestamp())

    class Meta:
        model = Post
        fields = (
            "id",
            "all_images",
            "insta_url",
            "name",
            "description",
            "created_at",
            "updated_at",
            "all_products",
        )


class PostUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField()


class ProductUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=255)
    price = serializers.FloatField()
    options = serializers.DictField()


class ProductCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    price = serializers.FloatField()
    options = serializers.DictField()
