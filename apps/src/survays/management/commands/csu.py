import os

from django.core.management import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    """Создание суперпользователя."""

    def handle(self, *args, **options):
        username = os.getenv("ADMIN_USERNAME")
        password = os.getenv("ADMIN_PASSWORD")

        try:
            user = User.objects.create_superuser(
                username=username,
            )
            user.set_password(password)
            user.save()
        except Exception:
            self.stdout.write(self.style.ERROR("SUPERUSER CREATE FAILED"))
        else:
            self.stdout.write(self.style.SUCCESS("SUPERUSER CREATE SUCCESS"))
