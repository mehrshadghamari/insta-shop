from abc import ABC
from abc import abstractmethod
from random import choice

import requests


class InstagramFetchStrategy(ABC):
    @abstractmethod
    def fetch_data(self, shortcode):
        pass


class Instagram230FetchStrategy(InstagramFetchStrategy):
    def fetch_data(self, shortcode):
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
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch from instagram230: {e}")


class RocketapiFetchStrategy(InstagramFetchStrategy):
    def fetch_data(self, shortcode):
        url = "https://rocketapi-for-instagram.p.rapidapi.com/instagram/media/get_info_by_shortcode"

        payload = {"shortcode": shortcode}
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": "346836d01cmshc9bf626dafcbebcp111cebjsn3ee0b3356736",
            "X-RapidAPI-Host": "rocketapi-for-instagram.p.rapidapi.com",
        }

        response = requests.post(url, json=payload, headers=headers)
        return response.json()["response"]["body"]["items"][0]


class InstagramMediaFetchStrategy(InstagramFetchStrategy):
    def fetch_data(self, shortcode):
        url = "https://instagram-media-api.p.rapidapi.com/media/shortcode"

        payload = {"shortcode": shortcode}
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": "346836d01cmshc9bf626dafcbebcp111cebjsn3ee0b3356736",
            "X-RapidAPI-Host": "instagram-media-api.p.rapidapi.com",
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()["items"][0]


class InstagramFetchStrategyFactory:
    def __init__(self):
        self.strategies = [
            Instagram230FetchStrategy(),
            RocketapiFetchStrategy(),
            InstagramMediaFetchStrategy(),
        ]

    def fetch_data(self, shortcode):
        strategies = self.strategies[:]
        while strategies:
            strategy = choice(strategies)
            try:
                return strategy.fetch_data(shortcode)
            except Exception as e:
                print(f"Fetching with {strategy.__class__.__name__} failed: {e}")
                strategies.remove(strategy)
        raise Exception("All strategies failed.")
