from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

# Apps y modelos a cubrir
MODELS = {
    # app_label: [model_name, ...]
    "customers": ["Customer"],
    "vehicles": ["Vehicle"],
    "catalog": ["Service", "Part"],
    "workorders": ["WorkOrder", "WorkOrderService", "WorkOrderPart"],
}

# Mapa permisos por rol
# Nota: DjangoModelPermissions evalúa add/change/delete/view en función del método HTTP
ROLE_PERMS = {
    "Admin": {
        "customers": ["add", "change", "delete", "view"],
        "vehicles": ["add", "change", "delete", "view"],
        "catalog": ["add", "change", "delete", "view"],
        "workorders": ["add", "change", "delete", "view"],
    },
    # Asesor: puede crear y ver todo lo operativo (lo que piden los tests)
    "Asesor": {
        "customers": ["add", "change", "view"],
        "vehicles": ["add", "change", "view"],
        "catalog": ["add", "change", "view"],  # <- add Service/Part para pasar el test
        "workorders": ["add", "change", "view"],
    },
    # Mecánico: puede ver (y actualizar detalle de WO si quisieras; los tests solo piden que NO borre vehicle)
    "Mecanico": {
        "customers": ["view"],
        "vehicles": ["view"],
        "catalog": ["view"],
        "workorders": ["view", "change"],
    },
}

def perm_codename(action, model):
    return f"{action}_{model.lower()}"

def ensure_group(name):
    group, _ = Group.objects.get_or_create(name=name)
    return group

def set_group_perms(group, wanted_perms):
    """
    wanted_perms: dict app_label -> set(codenames)
    """
    all_codes = set()
    for app_label, codes in wanted_perms.items():
        for code in codes:
            all_codes.add((app_label, code))

    # Resolver Permission objs existentes
    to_add = []
    for app_label, code in all_codes:
        try:
            perm = Permission.objects.get(content_type__app_label=app_label, codename=code)
            to_add.append(perm)
        except Permission.DoesNotExist:
            # Silencioso si aún no existen (p.e. durante migraciones incompletas)
            pass

    # Limpiamos las del mismo scope (solo de los app_labels que tocamos)
    app_labels = set(wanted_perms.keys())
    qs_existing = group.permissions.filter(content_type__app_label__in=app_labels)
    group.permissions.remove(*list(qs_existing))

    if to_add:
        group.permissions.add(*to_add)

class Command(BaseCommand):
    help = "Crea/actualiza roles (grupos) y asigna permisos por modelo"

    def handle(self, *args, **options):
        # Asegurar que existan ContentTypes (las migraciones ya han corrido en tests)
        # Construir todas las codenames deseadas
        wanted_by_group = {}
        for role, app_map in ROLE_PERMS.items():
            wanted_by_group[role] = {}
            for app_label, actions in app_map.items():
                # Reunir modelos del app
                models = MODELS.get(app_label, [])
                codes = set()
                for m in models:
                    for action in actions:
                        codes.add(perm_codename(action, m))
                wanted_by_group[role][app_label] = codes

        # Crear grupos y asignar permisos
        for role in wanted_by_group.keys():
            group = ensure_group(role)
            set_group_perms(group, wanted_by_group[role])

        # (Opcional) feedback
        for role, per_app in wanted_by_group.items():
            total = sum(len(v) for v in per_app.values())
            self.stdout.write(f"✔ {role}: {total} permisos asignados.")
        self.stdout.write("🎯 Roles creados/actualizados con éxito.")
