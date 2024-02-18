import json
from typing import Any
from typing import Dict
from typing import List
from typing import Union

from openai import OpenAI
from pydantic import ValidationError

from helpers.pydantic.models import Product


def generate_data(caption: str, max_attempts: int = 3) -> Union[List[Dict[str, Any]], None]:
    api_key = "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"
    client = OpenAI(api_key=api_key)
    attempts = 0

    while attempts < max_attempts:
        try:
            completion = client.chat.completions.create(
                model="ft:gpt-3.5-turbo-1106:personal::8sdYOUGZ",
                messages=[
                    {
                        "role": "system",
                        "content": 'Always extract a valid stringify array of JSONs without extra spaces and new lines. The Response structure should exactly like  : [{"name":"the product name","sku":"the product code","price":"the product before discount price","final_price":"final and after discount price of the product","options":{"colors":["color1","color2"],"sizes":["size1","size2"]}}]',
                    },
                    {"role": "user", "content": caption},
                ],
            )
            content = completion.choices[0].message.content
            products_data = json.loads(content)

            # Validate each product in the list using the Pydantic model
            validated_products = [Product(**product) for product in products_data]
            # Convert validated products to a list of dictionaries
            products_dicts = [product.model_dump() for product in validated_products]
            return products_dicts  # Return list of dictionaries

        except (json.JSONDecodeError, ValidationError):
            attempts += 1  # Increment attempts counter on failure
            print(f"Attempt {attempts}/{max_attempts} failed. Retrying...")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    print("Maximum attempts reached. No valid data received.")
    return None  # Return None if valid data could not be obtained after max_attempts
