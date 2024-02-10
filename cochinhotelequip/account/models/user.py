
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
)
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    def create_user(self, username, password, **extra_fields):
        """
        Normal user creation.
        Returns: User instance
        """
        if not username:
            raise ValueError(_("The Username must be set"))

        if extra_fields.get("email"):
            extra_fields["email"] = self.normalize_email(
                extra_fields.get("email")
            ).lower()

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Superuser creation.
        Returns User instance
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser,):

    """
    User creation required fields
    """

    email = models.EmailField(max_length=255, blank=True)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128, blank=True)
    display_name = models.CharField(max_length=50, null=True)
    username = models.CharField(max_length=255, unique=True, null=True)
    phone = PhoneNumberField(unique=False, null=True, blank=True)
    gst_cus = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    remarks = models.CharField(max_length=50, null=True)
    created_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_by_user",
    )
    modified_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="modified_by_user",
    )

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name"]

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def get_phone_as_list(self):
        return (
            [f"+{self.phone.country_code}", self.phone.national_number]
            if self.phone
            else None
        )
