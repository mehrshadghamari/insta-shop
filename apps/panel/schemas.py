from drf_spectacular.utils import extend_schema

from apps.panel.serializers import ShopSerializer

shop_detail_view_schema = extend_schema(
    operation_id="get_shop_details",
    tags=["Shops"],
    summary="Get Shop Details",
    description="Retrieves detailed information about a specific shop, including shop info, payment info, and subscriptions.",
    responses={200: ShopSerializer, 404: {"description": "Shop not found"}},
    parameters=[
        {
            "name": "domain",
            "in": "path",
            "required": True,
            "description": "Domain of the shop to retrieve.",
            "schema": {"type": "string"},
        }
    ],
)
