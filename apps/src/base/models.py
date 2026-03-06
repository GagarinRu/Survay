from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Manager

NULLABLE = {"blank": True, "null": True}


class BaseModel(models.Model):
    """Base model"""

    objects: Manager
    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)

    class Meta:
        abstract = True


class LowerCaseEmailField(models.EmailField):
    """Email in lowercase."""

    def get_prep_value(self, value: str) -> str | None:
        if value:
            return str(value).lower()
