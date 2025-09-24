# core/management/commands/ensure_test_user.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = "Crea/actualiza el usuario de pruebas 'caprivas' y lo asigna al grupo 'asesor'."

    def handle(self, *args, **options):
        User = get_user_model()
        username = "caprivas"
        password = "Wolf2574$"
        email = "caprivas@example.com"

        user, created = User.objects.get_or_create(username=username, defaults={"email": email})
        user.set_password(password)
        user.is_active = True
        user.save()

        asesor, _ = Group.objects.get_or_create(name="asesor")
        user.groups.add(asesor)
        self.stdout.write(self.style.SUCCESS(f"✔ Usuario de pruebas '{username}' listo y en grupo 'asesor'."))
