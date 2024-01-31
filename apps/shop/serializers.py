from rest_framework import serializers

from apps.shop.models import ImageModel
from apps.shop.models import Post
from apps.shop.models import Product
from apps.shop.models import ProductOptionType
from apps.shop.models import ProductVariant



class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id','insta_url','name','description')