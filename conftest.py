# backend/conftest.py
import uuid
import pytest
from django.contrib.auth.models import Group, Permission, User
from rest_framework.test import APIClient

@pytest.fixture(autouse=True, scope="session")
def _ensure_groups_and_perms(django_db_setup, django_db_blocker):
    # Asegura grupos y permisos finos de quotes
    with django_db_blocker.unblock():
        for g in ("Admin", "Asesor", "Mecanico"):
            Group.objects.get_or_create(name=g)
        for codename in [
            "send_quotation", "approve_quotation",
            "reject_quotation", "convert_quotation_to_workorder"
        ]:
            Permission.objects.filter(codename=codename).first()

@pytest.fixture
def api():
    return APIClient()

@pytest.fixture
def user_factory(db):
    def _make(groups=()):
        uname = f"u_{uuid.uuid4().hex[:10]}"
        u = User.objects.create_user(username=uname, password="secret123")
        for g in groups:
            u.groups.add(Group.objects.get(name=g))
        return u
    return _make

@pytest.fixture
def auth_api(api, user_factory):
    def _login(group_name="Asesor"):
        u = user_factory(groups=(group_name,))
        api.force_authenticate(user=u)
        return api, u
    return _login
