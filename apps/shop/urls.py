from django.conf.urls.static import static
from django.urls import path

from insta_shop import settings

from . import views

urlpatterns = [
    path("insta-api/", views.GetFromInsta.as_view(), name="instal-api"),
    path("post-list/", views.PostList.as_view(), name="post-list"),
    path("post-detail/<int:pk>/", views.PostDetail.as_view(), name="post-detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
