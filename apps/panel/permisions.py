from rest_framework.permissions import BasePermission


class IsShopManager(BasePermission):
    def has_permission(self, request, view):
        # return ShopUser.objects.filter(user=request.user.id, shop=request.shop.id).exists()
        return True
