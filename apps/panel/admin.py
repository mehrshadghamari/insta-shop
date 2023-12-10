# Register your models here.
from django.contrib import admin
from apps.panel.models import User , ShopUser , ShopInfo , PaymentInfo , Subscription , SubscriptionType , Shop


admin.site.register(User)
admin.site.register(ShopUser)
admin.site.register(ShopInfo)
admin.site.register(PaymentInfo)
admin.site.register(Subscription)
admin.site.register(SubscriptionType)
admin.site.register(Shop)

