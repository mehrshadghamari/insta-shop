from django.core.management.base import BaseCommand

from apps.panel.models import PaymentInfo
from apps.panel.models import Shop
from apps.panel.models import ShopInfo
from apps.panel.models import Subscription
from apps.panel.models import SubscriptionType
from apps.panel.models import UserProfile


class Command(BaseCommand):
    help = "Deletes all shop-related data from the database"

    def handle(self, *args, **kwargs):
        # Ask for confirmation
        confirm = input(
            "Are you sure you want to delete all shop data? This cannot be undone. Type 'yes' to continue: "
        )
        if confirm.lower() != "yes":
            self.stdout.write(self.style.WARNING("Aborted: Data deletion cancelled."))
            return

        # Delete data from each model
        Subscription.objects.all().delete()
        SubscriptionType.objects.all().delete()
        PaymentInfo.objects.all().delete()
        ShopInfo.objects.all().delete()
        Shop.objects.all().delete()
        UserProfile.objects.filter(is_staff=False, is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS("Successfully deleted all shop-related data."))
