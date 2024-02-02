from django.urls import path

from . import views

urlpatterns = [
    path("insta-api/", views.GetFromInsta.as_view(), name="instal-api"),
    path("post-list/", views.PostList.as_view(), name="post-list"),
    path("post-detail/<int:pk>", views.PostDetail.as_view(), name="post-detail"),
]
