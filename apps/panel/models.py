from django.db import models
from django.contrib.auth.models import AbstractUser


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True



class UserProfile(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    national_code = models.CharField(max_length=20, blank=True, null=True, db_index=True)




class Shop(TimeStampedModel):
    domain = models.URLField(unique=True, db_index=True)


    def __str__(self):
        return f"{self.domain}"
    


class ShopUser(TimeStampedModel):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE,related_name="admins")
    is_owner = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)


    class Meta:
        unique_together = ['user', 'shop']

    def __str__(self):
        role = "Owner" if self.is_owner else "Manager"
        return f"{self.user.username} in {self.shop} as {role}"
    

class Customer(TimeStampedModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="customers")


    class Meta:
        unique_together = ['user', 'shop']
    
    def __str__(self):
        return f"{self.user.username} in {self.shop}"


class ShopInfo(TimeStampedModel):
    shop = models.OneToOneField(Shop, on_delete=models.CASCADE, related_name='info')
    name = models.CharField(max_length=255)
    description = models.TextField()
    address = models.TextField()
    logo = models.ImageField(upload_to='logos/')
    instagram_page = models.URLField(blank=True, null=True)
    web_color = models.CharField(max_length=7) 

    def __str__(self):
        return self.name


class PaymentInfo(TimeStampedModel):
    shop = models.OneToOneField(Shop, on_delete=models.CASCADE, related_name='payment')
    bank_card = models.CharField(max_length=16)
    merchant_id = models.CharField(max_length=32)



class SubscriptionType(TimeStampedModel):
    name = models.CharField(max_length=100)
    limit_request = models.CharField(max_length=100)


class Subscription(TimeStampedModel):
    shop = models.OneToOneField(Shop, on_delete=models.CASCADE, related_name='subscription')
    start_date = models.DateField()
    end_date = models.DateField()
    type = models.ForeignKey(SubscriptionType,on_delete=models.DO_NOTHING)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"'subscription"
    








