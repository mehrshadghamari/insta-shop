from django.urls import path

from . import views

urlpatterns = [
    path("shop/<str:domain>/", views.ShopDetailView.as_view(), name="shop-detail"),
]
