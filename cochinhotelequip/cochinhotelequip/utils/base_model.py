
from django.contrib.auth import get_user_model

# lib imports
from django.db import models
from django.utils.translation import gettext_lazy as _

USER = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(verbose_name=_("Created At"), auto_now_add=True)
    modified_at = models.DateTimeField(verbose_name=_("Modified At"), auto_now=True)
    created_by = models.ForeignKey(
        USER,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_created_by_user",
    )
    modified_by = models.ForeignKey(
        USER,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_modified_by_user",
    )

    class Meta:
        abstract = True
        ordering = ["-modified_at"]
