from django.db.models import Prefetch
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.panel.models import Shop
from apps.panel.models import Subscription
from apps.panel.serializers import ShopSerializer


class ShopDetailView(APIView):
    def get(self, request, domain):
        shop = (
            Shop.objects.filter(domain=domain)
            .select_related("info")
            .prefetch_related(
                "payment_set", Prefetch("subscription_set", queryset=Subscription.objects.select_related("type"))
            )
            .first()
        )

        if not shop:
            return Response({"error": "Shop not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ShopSerializer(shop)
        return Response(serializer.data, status=status.HTTP_200_OK)
