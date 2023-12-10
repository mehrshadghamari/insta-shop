from rest_framework.permissions import BasePermission

from apps.panel.models import ShopUser


class IsShopManager(BasePermission):
    def has_permission(self, request, view):
        custom_shop_id = 2
        custom_user_id = 2
        return bool(ShopUser.objects.filter(user=custom_user_id, shop=custom_shop_id).first())
