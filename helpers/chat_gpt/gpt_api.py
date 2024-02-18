import json

from openai import OpenAI


def generate_data(caption):
    api_key = "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"
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-1106:personal::8sdYOUGZ",
        messages=[
            {
                "role": "system",
                "content": 'Always extract a valid stringify array of JSONs without extra spaces and new lines. The Response structure should exactly like  : [{"name":"the product name","sku":"the product code","price":"the product before discount price","final_price":"final and after discount price of the product","options":{"colors":["color1","color2"],"sizes":["size1","size2"]}}]',
            },
            {"role": "user", "content": f"{caption}"},
        ],
    )
    content = completion.choices[0].message.content
    products = json.dumps(content)
    return json.loads(products)
