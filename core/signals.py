from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.db.models import Q


def _get_perms_for(app_label: str, model_names: list[str], actions: list[str]):
    """
    Regresa objetos Permission para un app_label dado,
    combinando acciones (add/change/delete/view) con los codenames del modelo.
    """
    wanted_codenames = []
    for m in model_names:
        for a in actions:
            wanted_codenames.append(f"{a}{m}")
    return list(
        Permission.objects.filter(
            content_type__app_label=app_label, codename__in=wanted_codenames
        )
    )


def _ensure_user(username: str, password: str, group_name: str):
    User = get_user_model()
    u, created = User.objects.get_or_create(username=username)
    if created or not u.check_password(password):
        u.set_password(password)
        u.is_active = True
        u.save()
    g = Group.objects.get(name=group_name)
    u.groups.set([g])
    u.save()
    return u


@receiver(post_migrate)
def seed_rbac(sender, app_config, **kwargs):
    """
    Se ejecuta después de CADA migrate de cualquier app.
    Idempotente: si algo ya existe, solo se asegura de dejarlo bien.

    Ventaja: las tablas (auth_group, permissions, contenttypes, etc.) ya existen
    cuando corre esta señal, evitando 'no such table'.
    """
    # Apps donde tenemos modelos reales
    MODELOS = {
        "customers": ["customer"],
        "vehicles": ["vehicle"],
        "workorders": ["workorder"],
        "catalog": ["stockitem", "service"],
    }

    # Asegurar grupos
    admin_group, _ = Group.objects.get_or_create(name="Admin")
    asesor_group, _ = Group.objects.get_or_create(name="Asesor")
    mecanico_group, _ = Group.objects.get_or_create(name="Mecanico")

    # Admin: todos los permisos de estos apps
    all_perms = Permission.objects.filter(
        content_type__app_label__in=list(MODELOS.keys())
    )
    admin_group.permissions.set(all_perms)

    # Asesor: view/add/change en todos los modelos del dominio
    P_VIEW, P_ADD, P_CHANGE = "view_", "add_", "change_"
    asesor_perms = []
    for app_label, models in MODELOS.items():
        asesor_perms += _get_perms_for(app_label, models, [P_VIEW, P_ADD, P_CHANGE])
    asesor_group.permissions.set(asesor_perms)

    # Mecánico: solo view (ajusta si quieres que cambie OT)
    mecanico_perms = []
    for app_label, models in MODELOS.items():
        mecanico_perms += _get_perms_for(app_label, models, [P_VIEW])
    # Ejemplo si quieres permitir editar workorders:
    # mecanico_perms += _get_perms_for("workorders", ["workorder"], ["change_"])
    mecanico_group.permissions.set(mecanico_perms)

    # Usuarios de prueba (los que usan tus tests)
    _ensure_user("asesor_test", "asesor123", "Asesor")
    _ensure_user("mecanico_test", "mecanico123", "Mecanico")
    _ensure_user("admin_test", "admin123", "Admin")

    # Tu usuario manual
    _ensure_user("caprivas", "Wolf2574$", "Asesor")
