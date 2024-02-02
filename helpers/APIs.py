import requests


def fetch_instagram_data(shortcode):
    """Fetch Instagram data using the shortcode."""
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
