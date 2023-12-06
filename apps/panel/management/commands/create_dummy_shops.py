import random
import string

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.panel.models import PaymentInfo
from apps.panel.models import Shop
from apps.panel.models import ShopInfo
from apps.panel.models import Subscription
from apps.panel.models import SubscriptionType
from apps.panel.models import UserProfile


class Command(BaseCommand):
    help = "Generate dummy data for 200 shops"

    def handle(self, *args, **kwargs):
        for i in range(200):
            # Create a user profile
            username = f"user_{i}"
            UserProfile.objects.create(
                username=username,
                email=f"{username}@example.com",
                phone_number=self.random_phone_number(),
                national_code=self.random_national_code(),
            )

            # Create a shop
            domain = f"shop{i}.example.com"
            shop = Shop.objects.create(domain=domain)

            # Create shop info
            ShopInfo.objects.create(
                shop=shop,
                name=f"Shop {i}",
                description=f"Description for Shop {i}",
                address=f"123, Some Street{i}, City{i}, Country{i}",
                logo=self.random_logo_path(),
                instagram_page=f"https://instagram.com/shop{i}",
                web_color=self.random_hex_color(),
            )

            # Create payment info
            PaymentInfo.objects.create(
                shop=shop, bank_card=self.random_bank_card_number(), merchant_id=self.random_merchant_id()
            )

            # Create subscription
            subscription_type, _ = SubscriptionType.objects.get_or_create(
                name=random.choice(["Basic", "Premium", "Gold"]), limit_request=str(random.randint(100, 1000))
            )
            Subscription.objects.create(
                shop=shop,
                type=subscription_type,
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timezone.timedelta(days=365),
                is_active=random.choice([True, False]),
            )

        self.stdout.write(self.style.SUCCESS("Successfully generated dummy data for 200 shops"))

    def random_phone_number(self):
        return "".join(random.choice(string.digits) for _ in range(10))

    def random_national_code(self):
        return "".join(random.choice(string.digits) for _ in range(10))

    def random_logo_path(self):
        return f"logos/shop_logo_{random.randint(1, 200)}.png"

    def random_hex_color(self):
        return f'#{"".join(random.choice(string.hexdigits) for _ in range(6))}'

    def random_bank_card_number(self):
        return "".join(random.choice(string.digits) for _ in range(16))

    def random_merchant_id(self):
        return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
