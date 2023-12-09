from rest_framework import serializers

from apps.panel.models import PaymentInfo
from apps.panel.models import Shop
from apps.panel.models import ShopInfo
from apps.panel.models import Subscription
from apps.panel.models import SubscriptionType


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
