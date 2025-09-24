import os
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

# Permisos por modelo que usaremos
MODELS_FOR_RBAC = [
    ("customers", "customer"),
    ("vehicles", "vehicle"),
    ("workorders", "workorder"),
    ("catalog", "service"),
    ("catalog", "stockitem"),  # Part es proxy -> permisos del modelo base
]

# Mapeos de permisos por rol
# Nota: view_* siempre va incluido para que las listas funcionen
ADMIN_PERMS = {"add", "change", "delete", "view"}
ASESOR_PERMS = {
    # puede ver todo
    "view",
    # puede crear/editar clientes, vehículos, órdenes, servicios y piezas
    "add", "change",
}
MECANICO_PERMS = {
    # puede ver todo, pero sin add/change/delete
    "view",
}

def _ensure_perms(group: Group, perm_set: set[str]):
    """Asigna al grupo los permisos solicitados sobre los modelos de MODELS_FOR_RBAC."""
    for app_label, model in MODELS_FOR_RBAC:
        try:
            ct = ContentType.objects.get(app_label=app_label, model=model)
        except ContentType.DoesNotExist:
            continue
        for action in perm_set:
            codename = f"{action}_{model}"
            try:
                perm = Permission.objects.get(content_type=ct, codename=codename)
            except Permission.DoesNotExist:
                continue
            group.permissions.add(perm)


def seed_rbac(**kwargs):
    """
    Siembra grupos y (opcionalmente) usuarios.
    - Siempre crea/actualiza grupos y asigna permisos.
    - Solo crea usuarios si NO estamos en test (controlado por env).
    """
    # 1) Grupos
    admin_group, _ = Group.objects.get_or_create(name="Admin")
    asesor_group, _ = Group.objects.get_or_create(name="Asesor")
    mecanico_group, _ = Group.objects.get_or_create(name="Mecanico")

    # Limpiamos permisos actuales y reasignamos (idempotente)
    admin_group.permissions.clear()
    asesor_group.permissions.clear()
    mecanico_group.permissions.clear()

    _ensure_perms(admin_group, ADMIN_PERMS)
    _ensure_perms(asesor_group, ASESOR_PERMS)
    _ensure_perms(mecanico_group, MECANICO_PERMS)

    print("✔ Admin: permisos asignados.")
    print("✔ Asesor: permisos asignados.")
    print("✔ Mecanico: permisos asignados.")
    print("🎯 Roles creados/actualizados con éxito.")

    # 2) Usuarios (omitir en tests)
    # Coloca esta variable en test_settings; si está definida, no creamos usuarios
    if os.environ.get("DISABLE_USER_SEED") == "1":
        return

    # Usuarios de ejemplo SOLO para entornos no-test
    # (si ya existen, no falla; get_or_create es idempotente)
    admin_user, _ = User.objects.get_or_create(username="admin_seed")
    if not admin_user.has_usable_password():
        admin_user.set_password("admin123")
        admin_user.save()
    admin_user.groups.add(admin_group)

    asesor_user, _ = User.objects.get_or_create(username="asesor_seed")
    if not asesor_user.has_usable_password():
        asesor_user.set_password("asesor123")
        asesor_user.save()
    asesor_user.groups.add(asesor_group)

    mecanico_user, _ = User.objects.get_or_create(username="mecanico_seed")
    if not mecanico_user.has_usable_password():
        mecanico_user.set_password("mecanico123")
        mecanico_user.save()
    mecanico_user.groups.add(mecanico_group)

    print("👤 Usuarios seed creados (entorno no-test).")
