from drf_spectacular.utils import extend_schema

from apps.panel.serializers import PaymentInfoSerializer
from apps.panel.serializers import ShopDetailSerializer
from apps.panel.serializers import ShopInfoDetailSerializer
from apps.panel.serializers import ShopInfoSerializer
from apps.panel.serializers import ShopPaymentDetailSerializer
from apps.panel.serializers import ShopSubscriptionDetailSerializer

# Shop Detail View
shop_detail_view_schema = extend_schema(
    operation_id="get_shop_details",
    tags=["Shops"],
    summary="Get Shop Details",
    description="Retrieves detailed information about a specific shop, including shop info, payment info, and subscriptions.",
    responses={200: ShopDetailSerializer, 404: {"description": "Shop not found"}},
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

# Shop Info Detail View
shop_info_detail_view_schema = extend_schema(
    operation_id="get_shop_info_details",
    tags=["Shops"],
    summary="Get Shop Info Details",
    description="Retrieves information about the shop's info.",
    responses={200: ShopInfoDetailSerializer, 404: {"description": "Shop not found"}},
    parameters=[
        {
            "name": "domain",
            "in": "path",
            "required": True,
            "description": "Domain of the shop to retrieve info for.",
            "schema": {"type": "string"},
        }
    ],
)

# Shop Payment Detail View
shop_payment_detail_view_schema = extend_schema(
    operation_id="get_shop_payment_details",
    tags=["Shops"],
    summary="Get Shop Payment Details",
    description="Retrieves payment information for a specific shop.",
    responses={200: ShopPaymentDetailSerializer, 404: {"description": "Shop not found"}},
    parameters=[
        {
            "name": "domain",
            "in": "path",
            "required": True,
            "description": "Domain of the shop to retrieve payment details for.",
            "schema": {"type": "string"},
        }
    ],
)

# Shop Subscription Detail View
shop_subscription_detail_view_schema = extend_schema(
    operation_id="get_shop_subscription_details",
    tags=["Shops"],
    summary="Get Shop Subscription Details",
    description="Retrieves subscription details for a specific shop.",
    responses={200: ShopSubscriptionDetailSerializer, 404: {"description": "Shop not found"}},
    parameters=[
        {
            "name": "domain",
            "in": "path",
            "required": True,
            "description": "Domain of the shop to retrieve subscription details for.",
            "schema": {"type": "string"},
        }
    ],
)


# 'Create Shop Info'
create_shop_info_schema = extend_schema(
    operation_id="create_shop_info",
    tags=["Shop Information"],
    summary="Create Shop Information",
    description="Creates a new shop information record.",
    request=ShopInfoSerializer,
    responses={
        201: {"description": "Shop information successfully created.", "content": ShopInfoSerializer},
        400: {"description": "Invalid data provided"},
    },
)

# 'Update Shop Info'
update_shop_info_schema = extend_schema(
    operation_id="update_shop_info",
    tags=["Shop Information"],
    summary="Update Shop Information",
    description="Updates an existing shop information record.",
    request=ShopInfoSerializer,
    responses={
        200: {"description": "Shop information successfully updated.", "content": ShopInfoSerializer},
        400: {"description": "Invalid data provided"},
        404: {"description": "Shop information not found"},
    },
)


# Create PaymentInfo API
create_payment_info_schema = extend_schema(
    operation_id="create_payment_info",
    tags=["Payment Information"],
    summary="Create Payment Information",
    description="Creates a new payment information record.",
    request=PaymentInfoSerializer,
    responses={
        201: {"description": "Payment information successfully created.", "content": PaymentInfoSerializer},
        400: {"description": "Invalid data provided"},
    },
)


# Update PaymentInfo API
update_payment_info_schema = extend_schema(
    operation_id="update_payment_info",
    tags=["Payment Information"],
    summary="Update Payment Information",
    description="Updates an existing payment information record.",
    request=PaymentInfoSerializer,
    responses={
        200: {"description": "Payment information successfully updated.", "content": PaymentInfoSerializer},
        400: {"description": "Invalid data provided"},
        404: {"description": "Payment information not found"},
    },
)
