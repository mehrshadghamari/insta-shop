from django.conf.urls.static import static
from django.urls import path

from insta_shop import settings

from . import views

urlpatterns = [
    path("insta-api/", views.GetFromInsta.as_view(), name="instal-api"),
    path("post-list/", views.PostList.as_view(), name="post-list"),
    path("post-detail/<int:pk>/", views.PostDetail.as_view(), name="post-detail"),
    path("post-update/", views.PostUpdate.as_view(), name="post-update"),
    path("post-delete/", views.PostDelete.as_view(), name="post-delete"),
    path("product-update/", views.ProductUpdate.as_view(), name="product-update"),
    path("product-create/", views.ProductCreate.as_view(), name="product-create"),
    path("product-delete/", views.ProductDelete.as_view(), name="product-delete"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
