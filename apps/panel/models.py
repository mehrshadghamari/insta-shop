from django.db import models
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):
    pass




class Shop(models.Model):

    def __str__(self):
        return f"{self.id}"
    


class ShopUser(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    is_owner = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)

    def __str__(self):
        role = "Owner" if self.is_owner else "Manager"
        return f"{self.user.user.username} in {self.shop} as {role}"



class Customer(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop,on_delete=models.CASCADE,related_name="members")

    def __str__(self):
        return self.user.user.username
    


class ShopInfo(models.Model):
    shop = models.OneToOneField(Shop, on_delete=models.CASCADE, related_name='info')
    name = models.CharField(max_length=255)
    description = models.TextField()
    address = models.TextField()
    logo = models.ImageField(upload_to='logos/')
    domain = models.URLField()
    instagram_page = models.URLField(blank=True, null=True)
    web_color = models.CharField(max_length=7) 

    def __str__(self):
        return self.name


class PaymentInfo(models.Model):
    shop = models.OneToOneField(Shop, on_delete=models.CASCADE, related_name='payment')
    bank_card = models.CharField(max_length=16)
    merchant_id = models.CharField(max_length=32)


class SubscriptionType(models.Model):
    name = models.CharField(max_length=100)
    limit_request = models.CharField(max_length=100)


class Subscription(models.Model):
    shop = models.OneToOneField(Shop, on_delete=models.CASCADE, related_name='subscription')
    start_date = models.DateField()
    end_date = models.DateField()
    type = models.ForeignKey(SubscriptionType,on_delete=models.DO_NOTHING)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"'subscription"
    








