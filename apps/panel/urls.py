from django.urls import path

from . import views

urlpatterns = [
    path("shop/<str:domain>/", views.ShopDetailView.as_view(), name="shop-detail"),
    path("shop-info/<str:domain>/", views.ShopInfoDetailView.as_view(), name="shop-info-detail"),
    path("shop-payment/<str:domain>/", views.ShopPaymentDetailView.as_view(), name="shop-payment-detail"),
    path("shop-subscription/<str:domain>/", views.ShopSubscriptionDetail.as_view(), name="shop-subscription-detail"),
    path("shop-info/create/", views.CreateShopInfoView.as_view(), name="create-shop-info"),
    path("shop-info/update/<int:pk>/", views.UpdateShopInfoView.as_view(), name="update-shop-info"),
    path("payment-info/create/", views.CreatePaymentInfoView.as_view(), name="create-payment-info"),
    path("payment-info/update/<int:pk>/", views.UpdatePaymentInfoView.as_view(), name="update-payment-info"),
]
