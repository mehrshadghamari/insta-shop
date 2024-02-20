import re
import uuid
from datetime import datetime

import emoji


# Compile regular expressions for efficiency if the function is called frequently
phone_number_regex = re.compile(r"\b(?:0|\u06F0)(?:9|\u06F9)[\d\u06F0-\u06F9]{9}\b|\b(?:0|\u06F0)[\d\u06F0-\u06F9]{10,11}\b")
hashtag_regex = re.compile(r"#\S+")
extra_spaces_regex = re.compile(r"\s+")



def extract_shortcode(post_url):
    try:
        return post_url.split("/")[4]
    except IndexError:
        return None


def clean_caption(caption: str) -> str:
    """
    Cleans the given caption string by removing emojis, phone numbers (including Persian digits),
    hashtags, and extra spaces.

    Args:
    - caption (str): The original caption string.

    Returns:
    - str: The cleaned caption string.
    """
    # Remove emojis using the emoji library
    caption = emoji.replace_emoji(caption, replace="")
    
    # Remove phone numbers (standard and Persian digits)
    caption = phone_number_regex.sub("", caption)

    # Remove hashtags
    caption = hashtag_regex.sub("", caption)

    # Reduce multiple spaces to a single space
    caption = extra_spaces_regex.sub(" ", caption)

    return caption.strip()
