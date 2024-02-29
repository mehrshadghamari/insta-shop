import random

from django.db.models import Prefetch
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.panel.models import PaymentInfo
from apps.panel.models import Shop
from apps.panel.models import ShopInfo
from apps.panel.models import ShopUser
from apps.panel.models import Subscription
from apps.panel.models import User
from apps.panel.permisions import IsShopManager
from apps.panel.serializers import PaymentInfoSerializer
from apps.panel.serializers import ShopCreateSerializer
from apps.panel.serializers import ShopInfoDetailSerializer
from apps.panel.serializers import ShopInfoSerializer
from apps.panel.serializers import ShopPaymentDetailSerializer
from apps.panel.serializers import ShopSerializer
from apps.panel.serializers import ShopSubscriptionDetailSerializer
from apps.panel.serializers import ShopUserRegistrationCompletionSerializer
from apps.panel.serializers import UpdateShopInfoSerializer

from .schemas import create_payment_info_schema
from .schemas import create_shop_info_schema
from .schemas import shop_detail_view_schema
from .schemas import shop_info_detail_view_schema
from .schemas import shop_payment_detail_view_schema
from .schemas import shop_subscription_detail_view_schema
from .schemas import update_payment_info_schema
from .schemas import update_shop_info_schema


class ShopDetailView(APIView):
    permission_classes = [IsShopManager]

    @shop_detail_view_schema
    def get(self, request):
        shop = (
            Shop.objects.filter(id=request.shop.id)
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
    permission_classes = [IsShopManager]

    @shop_info_detail_view_schema
    def get(self, request):
        shop = Shop.objects.filter(id=request.shop.id).select_related("info").first()
        if not shop:
            return Response({"error": "Shop not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ShopInfoDetailSerializer(shop)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShopPaymentDetailView(APIView):
    permission_classes = [IsShopManager]

    @shop_payment_detail_view_schema
    def get(self, request):
        shop = Shop.objects.filter(id=request.shop.id).prefetch_related("payment_set").first()

        if not shop:
            return Response({"error": "Shop not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ShopPaymentDetailSerializer(shop)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShopSubscriptionDetail(APIView):
    permission_classes = [IsShopManager]

    @shop_subscription_detail_view_schema
    def get(self, request):
        shop = Shop.objects.filter(id=request.shop.id).prefetch_related(
            "payment_set", Prefetch("subscription_set", queryset=Subscription.objects.select_related("type"))
        )
        if not shop:
            return Response({"error": "Shop not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ShopSubscriptionDetailSerializer(shop)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateShopInfoView(APIView):
    permission_classes = [IsShopManager]

    @create_shop_info_schema
    def post(self, request):
        serializer = ShopInfoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateShopInfoView(APIView):
    # permission_classes = [IsShopManager]

    @update_shop_info_schema
    def patch(self, request):
        try:
            shop_info = ShopInfo.objects.get(shop=request.shop.id)
        except ShopInfo.DoesNotExist:
            return Response({"error": "ShopInfo not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateShopInfoSerializer(shop_info, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreatePaymentInfoView(APIView):
    permission_classes = [IsShopManager]

    @create_payment_info_schema
    def post(self, request):
        serializer = PaymentInfoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdatePaymentInfoView(APIView):
    permission_classes = [IsShopManager]

    @update_payment_info_schema
    def patch(self, request):
        try:
            payment_info = PaymentInfo.objects.get(shop=request.shop.id)
        except PaymentInfo.DoesNotExist:
            return Response({"error": "PaymentInfo not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PaymentInfoSerializer(payment_info, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


### shop panel login


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # Customizing JWt token claims
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["phone_number"] = user.phone_number
        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


def get_tokens_for_user(user):
    refresh = MyTokenObtainPairSerializer.get_token(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class ShopPanelLogin(APIView):
    def post(self, request):
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response({"message": "کاربر با این شماره موبایل ثبت نشده است."}, status=status.HTTP_404_NOT_FOUND)

        if not user.check_password(password):
            return Response({"message": "رمز عبور وارد شده صحیح نمی‌ باشد."}, status=status.HTTP_400_BAD_REQUEST)

        user_shops = ShopUser.objects.filter(user=user)
        if not user_shops.exists():
            return Response({"message": "کاربر پنل با این شماره موبایل وجود ندارد."}, status=status.HTTP_404_NOT_FOUND)

        shop_ids = user_shops.filter(shop__isnull=False).values_list("shop_id", flat=True)
        token = get_tokens_for_user(user)

        return Response({"token": token, "shops": list(shop_ids)}, status=status.HTTP_200_OK)


class ShopPanelRegisterOTP(APIView):
    def post(self, request):
        phone_number = request.data["phone_number"]
        try:

            user_obj = User.objects.get(phone_number=phone_number)

        except User.DoesNotExist:
            user_obj = User.objects.create(phone_number=phone_number)

        shop_user = ShopUser.objects.filter(user=user_obj).exists()
        if shop_user:
            return Response({"message": "کاربر پنل با این شماره موبایل وجود دارد"}, status=status.HTTP_400_BAD_REQUEST)

        code = random.randint(10000, 99999)

        # send with sms service

        user_obj.otp_code = code
        user_obj.save()

        return Response({"message": "کد با موفقیت ارسال شد.", "code": code}, status=status.HTTP_200_OK)


class ShopPanelRegisterVerifyOTP(APIView):
    def post(self, request):
        phone_number = request.data["phone_number"]
        code = request.data["code"]
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response({"message": "کاربر با این شماره موبایل ثبت نشده است."})

        otp_code = user.otp_code
        if int(code) != otp_code:
            return Response({"message": "کد وارد شده درست نیست"}, status=status.HTTP_403_FORBIDDEN)
        token = get_tokens_for_user(user)
        user.otp_code = None
        user.save()
        return Response(
            {
                "token": token,
            },
            status=status.HTTP_201_CREATED,
        )


class CompleteShopUserRegistration(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ShopUserRegistrationCompletionSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user.first_name = serializer.validated_data["first_name"]
            user.last_name = serializer.validated_data["last_name"]
            user.national_code = serializer.validated_data["national_code"]
            user.set_password(serializer.validated_data["password"])
            user.save()

            # Create a ShopUser instance with a null shop
            ShopUser.objects.create(user=user)

            return Response({"message": "ثبت نام کاربر پنل با موفقیت انجام شد."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyShops(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_obj = request.user
        shop_users = ShopUser.objects.filter(user=user_obj)

        if not shop_users.exists():
            return Response({"message": "کاربر پنل نیست"}, status=status.HTTP_401_UNAUTHORIZED)

        shop_ids = shop_users.filter(shop__isnull=False).values_list("shop_id", flat=True)
        shops = Shop.objects.filter(id__in=shop_ids)
        serializer = ShopSerializer(shops, many=True)

        return Response({"shops": serializer.data}, status=status.HTTP_200_OK)


class CreateShop(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ShopCreateSerializer(data=request.data)
        if serializer.is_valid():
            shop = serializer.save()
            user = request.user

            # Attempt to find an existing ShopUser with a null shop for this user
            shop_user = ShopUser.objects.filter(user=user, shop__isnull=True).first()

            if shop_user:
                # If found, update the shop_user instance with the new shop
                shop_user.shop = shop
                shop_user.save()
            else:
                # If not found, create a new ShopUser instance with the user and new shop
                ShopUser.objects.create(user=user, shop=shop)

            return Response(
                {"message": "فروشگاه با موفقیت ایجاد شد.", "shop_id": shop.id}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
