from apps.panel.models import Shop


class ShopParamMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the query parameter 'custom_param' exists
        shop_id = request.GET.get("shop")

        # Set the custom variable in the request object
        if shop_id is not None:
            # Set the custom variable in the request object
            request.shop = Shop.objects.get(id=shop_id)
        response = self.get_response(request)
        return response
