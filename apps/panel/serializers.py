from rest_framework import serializers

from apps.panel.models import PaymentInfo
from apps.panel.models import Shop
from apps.panel.models import ShopInfo
from apps.panel.models import ShopUser
from apps.panel.models import Subscription
from apps.panel.models import SubscriptionType
from apps.panel.validators import national_code_validator


class SubscriptionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionType
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    type = SubscriptionTypeSerializer()

    class Meta:
        model = Subscription
        fields = "__all__"


class PaymentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentInfo
        fields = "__all__"


class ShopInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopInfo
        fields = "__all__"


class UpdateShopInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopInfo
        fields = ["web_color", "name", "description"]


class ShopDetailSerializer(serializers.ModelSerializer):
    info = ShopInfoSerializer()
    payment = PaymentInfoSerializer(
        source="payment_set",
    )
    subscription = SubscriptionSerializer(
        source="subscription_set",
    )

    class Meta:
        model = Shop
        fields = [
            "id",
            "domain",
            "info",
            "payment",
            "subscription",
        ]


class ShopInfoDetailSerializer(serializers.ModelSerializer):
    info = ShopInfoSerializer()

    class Meta:
        model = Shop
        fields = [
            "id",
            "domain",
            "info",
        ]


class ShopPaymentDetailSerializer(serializers.ModelSerializer):
    payment = PaymentInfoSerializer(
        source="payment_set",
    )

    class Meta:
        model = Shop
        fields = [
            "id",
            "domain",
            "payment",
        ]


class ShopSubscriptionDetailSerializer(serializers.ModelSerializer):
    subscription = SubscriptionSerializer(
        source="subscription_set",
    )

    class Meta:
        model = Shop
        fields = [
            "id",
            "domain",
            "subscription",
        ]


class ShopUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopUser
        fields = ["shop"]


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        models = Shop
        fields = "__all__"


class ShopUserRegistrationCompletionSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=80)
    last_name = serializers.CharField(max_length=80)
    national_code = serializers.CharField(max_length=10, validators=[national_code_validator])
    password = serializers.CharField(write_only=True, style={"input_type": "password"})


class CreateShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopInfo
        fields = ["name", "description", "address", "logo", "instagram_page", "web_color"]


class ShopCreateSerializer(serializers.Serializer):
    domain = serializers.URLField()
    name = serializers.CharField(max_length=255)
    description = serializers.CharField()
    address = serializers.CharField()
    instagram_page = serializers.URLField(required=False, allow_blank=True)
    web_color = serializers.CharField()

    def create(self, validated_data):
        # Create the Shop instance
        shop = Shop.objects.create(domain=validated_data["domain"])

        # Create the ShopInfo instance associated with the Shop
        ShopInfo.objects.create(
            shop=shop,
            name=validated_data["name"],
            description=validated_data["description"],
            address=validated_data["address"],
            instagram_page=validated_data.get("instagram_page", ""),  # Handle optional field
            web_color=validated_data["web_color"],
        )

        return shop
