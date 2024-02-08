# Register your models here.
from django.contrib import admin

from apps.panel.models import PaymentInfo
from apps.panel.models import Shop
from apps.panel.models import ShopInfo
from apps.panel.models import ShopUser
from apps.panel.models import Subscription
from apps.panel.models import SubscriptionType,UserProfile
from apps.panel.models import User
from apps.panel.models import UserProfile

admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(ShopUser)
admin.site.register(ShopInfo)
admin.site.register(PaymentInfo)
admin.site.register(Subscription)
admin.site.register(SubscriptionType)
admin.site.register(Shop)
