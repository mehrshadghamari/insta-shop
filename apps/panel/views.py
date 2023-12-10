from django.db.models import Prefetch
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.panel.models import PaymentInfo
from apps.panel.models import Shop
from apps.panel.models import ShopInfo
from apps.panel.models import Subscription
from apps.panel.serializers import PaymentInfoSerializer
from apps.panel.serializers import ShopInfoDetailSerializer
from apps.panel.serializers import ShopInfoSerializer
from apps.panel.serializers import ShopPaymentDetailSerializer
from apps.panel.serializers import ShopSubscriptionDetailSerializer
from apps.panel.permisions import IsShopManager 

from .schemas import create_payment_info_schema
from .schemas import create_shop_info_schema
from .schemas import shop_detail_view_schema
from .schemas import shop_info_detail_view_schema
from .schemas import shop_payment_detail_view_schema
from .schemas import shop_subscription_detail_view_schema
from .schemas import update_payment_info_schema
from .schemas import update_shop_info_schema


class ShopDetailView(APIView):
    @shop_detail_view_schema
    def get(self, request):
        shop = (
            Shop.objects.filter(id=request.shop)
            .select_related("info")
            .prefetch_related(
                "payment_set", Prefetch("subscription_set", queryset=Subscription.objects.select_related("type"))
            )
            .first()
        )

        if not shop:
            return Response({"error": "Shop not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ShopInfoSerializer(shop)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShopInfoDetailView(APIView):
    # permission_classes = [IsShopManager]
    @shop_info_detail_view_schema
    def get(self, request):
        shop = Shop.objects.filter(id=request.shop).select_related("info").first()
        if not shop:
            return Response({"error": "Shop not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ShopInfoDetailSerializer(shop)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShopPaymentDetailView(APIView):
    @shop_payment_detail_view_schema
    def get(self, request):
        shop = Shop.objects.filter(id=request.shop).prefetch_related("payment_set").first()

        if not shop:
            return Response({"error": "Shop not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ShopPaymentDetailSerializer(shop)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShopSubscriptionDetail(APIView):
    @shop_subscription_detail_view_schema
    def get(self, request):
        shop = Shop.objects.filter(id=request.shop).prefetch_related(
            "payment_set", Prefetch("subscription_set", queryset=Subscription.objects.select_related("type"))
        )
        if not shop:
            return Response({"error": "Shop not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ShopSubscriptionDetailSerializer(shop)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateShopInfoView(APIView):
    @create_shop_info_schema
    def post(self, request):
        serializer = ShopInfoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateShopInfoView(APIView):
    @update_shop_info_schema
    def put(self, request, pk):
        try:
            shop_info = ShopInfo.objects.get(pk=pk)
        except ShopInfo.DoesNotExist:
            return Response({"error": "ShopInfo not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ShopInfoSerializer(shop_info, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreatePaymentInfoView(APIView):
    @create_payment_info_schema
    def post(self, request):
        serializer = PaymentInfoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdatePaymentInfoView(APIView):
    @update_payment_info_schema
    def put(self, request, pk):
        try:
            payment_info = PaymentInfo.objects.get(pk=pk)
        except PaymentInfo.DoesNotExist:
            return Response({"error": "PaymentInfo not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PaymentInfoSerializer(payment_info, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
