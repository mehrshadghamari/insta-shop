from rest_framework.permissions import BasePermission

from apps.panel.models import ShopUser


class IsShopManager(BasePermission):
    def has_permission(self, request, view):
        return bool(ShopUser.objects.filter(user=request.user, shop=request.shop.id).first())
