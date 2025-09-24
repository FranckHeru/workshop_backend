# core/apps.py
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.conf import settings


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        post_migrate.connect(seed_roles_and_data, sender=self)


def seed_roles_and_data(sender, **kwargs):
    """
    Crea/actualiza grupos y asigna permisos.
    NO crea registros de otras apps (p.ej., Customer) para evitar fallos
    cuando sus tablas aún no existen en la señal de core.
    """
    from django.contrib.auth.models import Group, Permission, User
    from django.contrib.contenttypes.models import ContentType

    # Recolecta permisos por app_label y modelo
    def perms_for(app_label, model_names):
        out = []
        for mn in model_names:
            try:
                ct = ContentType.objects.get(app_label=app_label, model=mn)
            except ContentType.DoesNotExist:
                continue
            out.extend(list(Permission.objects.filter(content_type=ct)))
        return out

    # Define permisos por rol (ajusta según tus necesidades actuales)
    admin_perms = Permission.objects.all()

    asesor_perms = []
    asesor_perms += perms_for("customers", ["customer"])
    asesor_perms += perms_for("vehicles", ["vehicle"])
    asesor_perms += perms_for("workorders", ["workorder", "worklog"])
    asesor_perms += perms_for("catalog", ["service", "part"])

    mecanico_perms = []
    # Mécanico: lectura de clientes/vehículos/servicios, crear worklogs, etc.
    # (Filtramos por codename para restringir create/delete donde aplique)
    for p in perms_for("customers", ["customer"]) + perms_for("vehicles", ["vehicle"]) + perms_for("catalog", ["service", "part"]):
        if p.codename.startswith("view_"):
            mecanico_perms.append(p)
    for p in perms_for("workorders", ["workorder"]):
        if p.codename.startswith("view_") or p.codename.startswith("change_"):
            mecanico_perms.append(p)
    for p in perms_for("workorders", ["worklog"]):
        # permitir crear/modificar sus logs (simplificado a add/change/view)
        if p.codename.startswith(("add_", "change_", "view_")):
            mecanico_perms.append(p)

    # Crea/actualiza grupos
    admin_group, _ = Group.objects.get_or_create(name="Admin")
    admin_group.permissions.set(admin_perms)

    asesor_group, _ = Group.objects.get_or_create(name="Asesor")
    asesor_group.permissions.set(asesor_perms)

    mecanico_group, _ = Group.objects.get_or_create(name="Mecanico")
    mecanico_group.permissions.set(mecanico_perms)

    print("✔ Admin: permisos asignados.")
    print("✔ Asesor: permisos asignados.")
    print("✔ Mecanico: permisos asignados.")
    print("🎯 Roles creados/actualizados con éxito.")

    # (Opcional) Si NO quieres crear usuarios en test, respeta un flag
    if getattr(settings, "DISABLE_USER_SEED", False):
        return

    # Crea usuarios demo (si no existe el flag anterior)
    admin_user, _ = User.objects.get_or_create(username="admin_test", defaults={"is_staff": True, "is_superuser": True})
    admin_user.set_password("admin123")
    admin_user.save()
    admin_user.groups.add(admin_group)

    asesor_user, _ = User.objects.get_or_create(username="asesor_test")
    asesor_user.set_password("asesor123")
    asesor_user.save()
    asesor_user.groups.set([asesor_group])

    mecanico_user, _ = User.objects.get_or_create(username="mecanico_test")
    mecanico_user.set_password("mecanico123")
    mecanico_user.save()
    mecanico_user.groups.set([mecanico_group])
