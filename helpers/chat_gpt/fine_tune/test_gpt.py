from openai import OpenAI

api_key = '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'

client = OpenAI(api_key=api_key)

completion = client.chat.completions.create(
  model="ft:gpt-3.5-turbo-1106:personal::8sdYOUGZ",
  messages=[
    {"role": "system", "content": "the list of available products in a instagram post with no space and stringified JSONs in an array like : '[{\"name\":\"the product name\",\"sku\":\"the product code\",\"price\":\"the product before discount price\",\"final_price\":\"final and after discount price of the product\",\"options\":{\"colors\":[\"color1\",\"color2\"],\"sizes\":[\"size1\",\"size2\"]}}]'"},
    {"role": "user", "content" : "ست ناز و خوشگل عیدونه پیچ از یفروش به صورت ست و تکی کفش عروسکی مدل پیچازی#جنس رویه سوییت و ورنیزیره پی یو فوق العاده سبک رکاب بندی داخل کیف آستری دوزی شده ی زیپ کوچیکم داره بند بلدم داره #جنس کیف و گلسر دقیقا از جنس کفش هست#جدول سایز بندی #سایز ۳۲ داخل کفش ۲۰.۵ سانت سایز ۳۳ داخل کفش ۲۱.۲ سانت سایز ۳۴ داخل کفش ۲۱.۷ سانت سایز ۳۵ داخل کفش ۲۲.۲ سانت سایز ۳۶ داخل کفش ۲۲.۶ سانت سایز ۳۷ داخل کفش ۲۳ سانت ابعاد کیف ارتفاع ۱۴ سانت عرض ۱۸ سانت قیمت کفش۶۴۰ت قیمت کیف ۴۴۰ت قشنگای من لطفا جدول سایز چک کنید و تو انتخابتون نهایت دقت"}
  ]
)
print(completion)




# {
#   "role": "system",
#   "content": "Extract and format product details from Instagram posts as a JSON array string. Each product entry should include the product's name, SKU (stock keeping unit), original price, discounted price (if applicable), and available options such as colors and sizes. Ensure no spaces are included in the JSON string, and all fields are accurately represented. Example format: '[{\"name\":\"ProductName\",\"sku\":\"ProductCode\",\"price\":\"OriginalPrice\",\"final_price\":\"DiscountedPrice\",\"options\":{\"colors\":[\"Color1\",\"Color2\"],\"sizes\":[\"Size1\",\"Size2\"]}}]'. Use placeholders for actual values and include all relevant details for each product."
# }