from django.urls import path

from . import views

urlpatterns = [
    path("shop/", views.ShopDetailView.as_view(), name="shop-detail"),
    path("shop-info/", views.ShopInfoDetailView.as_view(), name="shop-info-detail"),
    path("shop-payment/", views.ShopPaymentDetailView.as_view(), name="shop-payment-detail"),
    path("shop-subscription/", views.ShopSubscriptionDetail.as_view(), name="shop-subscription-detail"),
    path("shop-info/create/", views.CreateShopInfoView.as_view(), name="create-shop-info"),
    path("shop-info/update/", views.UpdateShopInfoView.as_view(), name="update-shop-info"),
    path("payment-info/create/", views.CreatePaymentInfoView.as_view(), name="create-payment-info"),
    path("payment-info/update/", views.UpdatePaymentInfoView.as_view(), name="update-payment-info"),
    path("shop/login/", views.ShopPanelLogin.as_view(), name="panel-login"),
    path("shop-user-register-otp/", views.ShopPanelRegisterOTP.as_view(), name="shop-user-register-otp"),
    path("shop-user-verify-otp/", views.ShopPanelRegisterVerifyOTP.as_view(), name="shop-user-verify-otp"),
    path(
        "shop-user-complete-registration/",
        views.CompleteShopUserRegistration.as_view(),
        name="shop-user-complete-registration",
    ),
    path("my-shops/", views.MyShops.as_view(), name="my-shops"),
    path("create-shop/", views.CreateShop.as_view(), name="create-shop"),
]
