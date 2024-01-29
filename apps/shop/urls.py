from django.urls import path

from . import views

urlpatterns = [
    path("insta-api/", views.GetFromInsta.as_view(), name="instal-api"),
]
