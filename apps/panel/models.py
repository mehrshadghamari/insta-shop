import random

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core import validators
from django.db import models
from django.utils import timezone

from apps.panel.validators import national_code_validator


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, phone_number, email, password, is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        user = self.model(
            phone_number=phone_number,
            username=username,
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            date_joined=now,
            **extra_fields,
        )

        if not extra_fields.get("no_password"):
            user.set_password(password)

        user.save(using=self._db)
        return user

    def create_user(self, username=None, phone_number=None, email=None, password=None, **extra_fields):
        if username is None:
            if email:
                username = email.split("@", 1)[0]
            if phone_number:
                username = random.choice("abcdefghijklmnopqrstuvwxyz") + str(phone_number)[-7:]
            while User.objects.filter(username=username).exists():
                username += str(random.randint(10, 99))

        return self._create_user(username, phone_number, email, password, False, False, **extra_fields)

    def create_superuser(self, username, phone_number, email, password, **extra_fields):
        return self._create_user(username, phone_number, email, password, True, True, **extra_fields)

    def get_by_phone_number(self, phone_number):
        return self.get(**{"phone_number": phone_number})


class User(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.
    Username, password and email are required. Other fields are optional.
    """

    username = models.CharField(
        ("username"),
        max_length=32,
        unique=True,
        null=True,
        blank=True,
        help_text=("Required. 30 characters or fewer starting with a letter. Letters, digits and underscore only."),
        validators=[
            validators.RegexValidator(
                r"^[a-zA-Z][a-zA-Z0-9_\.]+$",
                (
                    "Enter a valid username starting with a-z. "
                    "This value may contain only letters, numbers "
                    "and underscore characters."
                ),
                "invalid",
            ),
        ],
        error_messages={
            "unique": ("A user with that username already exists."),
        },
    )
    first_name = models.CharField(max_length=80, null=True)
    last_name = models.CharField(max_length=80, null=True)
    national_code = models.CharField(max_length=10, unique=True, null=True, validators=[national_code_validator])
    otp_code = models.IntegerField(null=True)

    email = models.EmailField(("email address"), unique=True, null=True, blank=True)
    phone_number = models.BigIntegerField(
        ("mobile number"),
        unique=True,
        null=True,
        validators=[
            validators.RegexValidator(r"^989[0-3,9]\d{8}$", ("Enter a valid mobile number."), "invalid"),
        ],
        error_messages={
            "unique": ("A user with this mobile number already exists."),
        },
    )
    is_staff = models.BooleanField(
        ("staff status"), default=False, help_text=("Designates whether the user can log into this admin site.")
    )
    is_active = models.BooleanField(
        ("active"),
        default=True,
        help_text=(
            "Designates whether this user should be treated as active. " "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(("date joined"), default=timezone.now)
    last_seen = models.DateTimeField(("last seen date"), null=True)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["email", "username"]

    class Meta:
        db_table = "users"
        verbose_name = "user"
        verbose_name_plural = "users"

    def ph_number(self):
        return str(self.phone_number)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if self.email is not None and self.email.strip() == "":
            self.email = None
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{str(self.phone_number)} - {self.full_name} "


# class UserProfile(User):
#     pass
# user = models.OneToOneField(User, on_delete=models.CASCADE)


class Shop(TimeStampedModel):
    domain = models.URLField(unique=True, db_index=True)

    def __str__(self):
        return f"{self.domain}"


class ShopUser(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, null=True, on_delete=models.CASCADE, related_name="admins")
    is_owner = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)

    class Meta:
        unique_together = ["user", "shop"]

    def __str__(self):
        role = "Owner" if self.is_owner else "Manager"
        return f"{self.user.username} in {self.shop} as {role}"


class Customer(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="customers")

    class Meta:
        unique_together = ["user", "shop"]

    def __str__(self):
        return f"{self.user.username} in {self.shop}"


class CustomerInfo(TimeStampedModel):
    user = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name="info")
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    national_code = models.CharField(max_length=10, unique=True, null=True, validators=[national_code_validator])


class ShopInfo(TimeStampedModel):
    shop = models.OneToOneField(Shop, on_delete=models.CASCADE, related_name="info")
    name = models.CharField(max_length=255)
    description = models.TextField()
    address = models.TextField()
    logo = models.ImageField(upload_to="logos/")
    instagram_page = models.URLField(blank=True, null=True)
    web_color = models.CharField(max_length=7)

    def __str__(self):
        return self.name


class PaymentInfo(TimeStampedModel):
    shop = models.OneToOneField(Shop, on_delete=models.CASCADE, related_name="payment")
    bank_card = models.CharField(max_length=16)
    merchant_id = models.CharField(max_length=32)


class SubscriptionType(TimeStampedModel):
    name = models.CharField(max_length=100)
    limit_request = models.CharField(max_length=100)


class Subscription(TimeStampedModel):
    shop = models.OneToOneField(Shop, on_delete=models.CASCADE, related_name="subscription")
    start_date = models.DateField()
    end_date = models.DateField()
    type = models.ForeignKey(SubscriptionType, on_delete=models.DO_NOTHING)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f" {Shop.id} subscription"
