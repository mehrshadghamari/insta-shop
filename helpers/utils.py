import re
import uuid
from datetime import datetime

import emoji


def extract_shortcode(post_url):
    try:
        return post_url.split("/")[4]
    except IndexError:
        return None


def generate_unique_filename(username):
    """Generate a unique file name for an image."""
    return f"image-shop:{username}-imgID:{uuid.uuid4().hex}-time:{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"


def clean_caption(caption: str) -> str:
    # Remove emojis using the emoji library
    caption = emoji.replace_emoji(caption, replace="")

    # Remove phone numbers (standard and Persian digits)
    caption = re.sub(r"\b(?:0|\u06F0)(?:9|\u06F9)[\d\u06F0-\u06F9]{9}\b", "", caption)
    caption = re.sub(r"\b(?:0|\u06F0)[\d\u06F0-\u06F9]{10,11}\b", "", caption)

    # Remove hashtags
    caption = re.sub(r"#\S+", "", caption)

    # Reduce multiple spaces to a single space
    caption = re.sub(r"\s+", " ", caption)

    return caption.strip()
