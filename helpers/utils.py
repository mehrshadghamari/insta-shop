import uuid
from datetime import datetime


def extract_shortcode(post_url):
    try:
        return post_url.split("/")[4]
    except IndexError:
        return None


def generate_unique_filename(username):
    """Generate a unique file name for an image."""
    return f"image-shop:{username}-imgID:{uuid.uuid4().hex}-time:{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
