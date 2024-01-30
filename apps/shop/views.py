import uuid
from datetime import datetime
from io import BytesIO

import requests
from django.core.files import File
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.shop.models import ImageModel
from apps.shop.models import Product
from helpers.functions import extract_shortcode
from helpers.functions import fetch_instagram_data
from helpers.functions import generate_unique_filename


class GetFromInsta(APIView):
    def post(self, request):
        shop = self.request.shop

        if not shop:
            return Response({"error": "shop ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        post_url = request.data.get("post_url")
        shortcode = extract_shortcode(post_url)

        if not shortcode:
            return Response({"error": "shortcode parameter is missing"}, status=status.HTTP_400_BAD_REQUEST)

        data = fetch_instagram_data(shortcode)

        if data is None:
            return Response({"error": "Failed to fetch Instagram data"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        images = [image["image_versions2"]["candidates"][0]["url"] for image in data.get("carousel_media", [])]
        caption = data.get("caption", {}).get("text", "")
        location = data.get("location", {}).get("name", "")
        like_count = data.get("like_count", None)

        # Extracting user information
        user_info = data.get("user", {})
        username = user_info.get("username", "")
        profile_pic_url = user_info.get("profile_pic_url", "")

        formatted_response = {
            "user_info": {
                "username": username,
                "profile_pic_url": profile_pic_url,
            },
            "caption": caption,
            "location": location,
            "like_count": like_count,
            "images": images,
        }
        ############################
        # use chatgpt for create product>>>

        if not images:
            return Response({"error": "No images found in the Instagram post"}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            product = Product.objects.create(shop=shop, name=f"From Instagram - {username}", description=caption)
            self.save_images_to_database(images, username, product)

        return Response(formatted_response, status=status.HTTP_200_OK)

    def save_images_to_database(self, images, username, product):
        image_models = []
        for image_url in images:
            response = requests.get(image_url)

            if response.status_code == 200:
                image_data = BytesIO(response.content)
                unique_filename = generate_unique_filename(username)

                # Create a new ImageModel instance
                product_image = ImageModel(content_object=product)
                product_image.image.save(unique_filename, File(image_data))
                image_models.append(product_image)

        ImageModel.objects.bulk_create(image_models)
