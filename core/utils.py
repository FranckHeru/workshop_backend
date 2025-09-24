import os
from django.core.management import call_command

_FLAG_ENV = "WORKSHOP_ROLES_SEEDED"

def run_seed_roles_once():
    """
    Ejecuta seed_roles solo una vez por proceso (útil en tests, runserver, etc.).
    Usa una variable de entorno como flag barata.
    """
    if os.environ.get(_FLAG_ENV) == "1":
        return
    call_command("seed_roles", verbosity=0)
    os.environ[_FLAG_ENV] = "1"
