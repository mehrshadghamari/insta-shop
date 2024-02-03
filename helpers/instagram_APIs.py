from abc import ABC
from abc import abstractmethod
from random import choice

import requests


class InstagramFetchStrategy(ABC):
    @abstractmethod
    def fetch_data(self, shortcode):
        pass


class RapidAPIFetchStrategy(InstagramFetchStrategy):
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
            raise Exception(f"Failed to fetch from RapidAPI: {e}")


class RapidAPI2FetchStrategy(InstagramFetchStrategy):
    def fetch_data(self, shortcode):
        raise NotImplementedError("This strategy is not implemented yet.")


class InstagramFetchStrategyFactory:
    def __init__(self):
        self.strategies = [RapidAPIFetchStrategy(), RapidAPI2FetchStrategy()]

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


# def fetch_instagram_data(shortcode):
#     """Fetch Instagram data using the shortcode."""
#     url = "https://instagram230.p.rapidapi.com/post/details"
#     querystring = {"shortcode": shortcode}
#     headers = {
#         "X-RapidAPI-Key": "346836d01cmshc9bf626dafcbebcp111cebjsn3ee0b3356736",
#         "X-RapidAPI-Host": "instagram230.p.rapidapi.com",
#     }

#     try:
#         response = requests.get(url, headers=headers, params=querystring)
#         response.raise_for_status()
#         return response.json()["data"]["xdt_api__v1__media__shortcode__web_info"]["items"][0]
#     except requests.exceptions.RequestException:
#         return None
