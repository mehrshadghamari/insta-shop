import uuid
from io import BytesIO

import requests
from django.core.files import File
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.shop.models import ImageModel


# Extract shortcode from Instagram URL
def extract_shortcode(post_url):
    parts = post_url.split("/")
    return parts[4]


# Fetch Instagram data using the shortcode
def fetch_instagram_data(shortcode):
    url = "https://instagram230.p.rapidapi.com/post/details"
    querystring = {"shortcode": shortcode}
    headers = {
        "X-RapidAPI-Key": "346836d01cmshc9bf626dafcbebcp111cebjsn3ee0b3356736",
        "X-RapidAPI-Host": "instagram230.p.rapidapi.com",
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        return response.json()["data"]["xdt_api__v1__media__shortcode__web_info"]["items"][0]
    except requests.exceptions.RequestException:
        return None


class GetFromInsta(APIView):
    def save_images_to_database(self, images, username):
        for image_url in images:
            response = requests.get(image_url)

            if response.status_code == 200:
                image_data = BytesIO(response.content)
                unique_filename = f"image_{username}_{uuid.uuid4().hex}.jpg"

                # Create a new ImageModel instance
                product_image = ImageModel()
                product_image.image.save(unique_filename, File(image_data))
                product_image.save()

    def post(self, request):
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

        # Save images to the database
        self.save_images_to_database(images, username)

        return Response(formatted_response, status=status.HTTP_200_OK)
