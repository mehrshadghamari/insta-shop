from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from apps.panel.models import Shop


class ShopMiddleware(MiddlewareMixin):
    def process_request(self, request):
        shop_id = request.GET.get("shop_id")

        if shop_id:
            try:
                request.shop = Shop.objects.get(id=shop_id)
            except Shop.DoesNotExist:
                return JsonResponse({"error": "Invalid shop ID"}, status=400)
        else:
            request.shop = None
