# core/management/commands/bootstrap_roles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

# Modelos a mapear para permisos base (add/change/delete/view)
MODELS = [
    ("customers", "Customer"),
    ("vehicles", "Vehicle"),
    ("catalog", "Service"),
    ("catalog", "Part"),
    ("quotes", "Quotation"),
    ("workorders", "WorkOrder"),
]

# Permisos finos específicos de cotizaciones
QUOTES_EXTRA_PERMS = [
    ("send_quotation", "Puede enviar cotización"),
    ("approve_quotation", "Puede aprobar cotización"),
    ("reject_quotation", "Puede rechazar cotización"),
    ("convert_quotation_to_workorder", "Puede convertir cotización a orden de trabajo"),
]

def get_ct(app_label, model_name):
    model = apps.get_model(app_label, model_name)
    return ContentType.objects.get_for_model(model)

class Command(BaseCommand):
    help = "Crea/actualiza grupos (Admin, Asesor, Mecanico) y asigna permisos."

    def handle(self, *args, **options):
        # 1) Crear permisos finos en quotes (si la app está disponible)
        try:
            ct_quotes = get_ct("quotes", "Quotation")
        except LookupError:
            self.stdout.write(self.style.WARNING("App 'quotes' no encontrada; salto permisos finos."))
            ct_quotes = None

        created_extra = []
        if ct_quotes:
            for codename, name in QUOTES_EXTRA_PERMS:
                p, created = Permission.objects.get_or_create(
                    content_type=ct_quotes,
                    codename=codename,
                    defaults={"name": name},
                )
                if created:
                    created_extra.append(codename)
        if created_extra:
            self.stdout.write(self.style.SUCCESS(f"Permisos finos creados: {created_extra}"))

        # 2) Armar lista de permisos por modelo
        perms_by_model = {}
        for app_label, model_name in MODELS:
            try:
                ct = get_ct(app_label, model_name)
            except LookupError:
                continue

            base_codenames = [
                f"add_{model_name.lower()}",
                f"change_{model_name.lower()}",
                f"delete_{model_name.lower()}",
                f"view_{model_name.lower()}",
            ]
            base = list(Permission.objects.filter(content_type=ct, codename__in=base_codenames))

            # Sumar finos a Quotation
            if app_label == "quotes" and model_name == "Quotation":
                base += list(Permission.objects.filter(
                    content_type=ct,
                    codename__in=[c for c, _ in QUOTES_EXTRA_PERMS]
                ))
            perms_by_model[(app_label, model_name)] = base

        # 3) Crear grupos
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        asesor_group, _ = Group.objects.get_or_create(name="Asesor")
        mecanico_group, _ = Group.objects.get_or_create(name="Mecanico")

        # 4) Admin = todos los permisos
        admin_group.permissions.set(Permission.objects.all())

        # 5) Asesor = CRUD Quotation + finos; view de maestros y OT
        asesor_perms = []
        for (app_label, model_name), perms in perms_by_model.items():
            for p in perms:
                code = p.codename
                if app_label == "quotes" and model_name == "Quotation":
                    if code.startswith(("add_", "change_", "view_")) or code in [c for c, _ in QUOTES_EXTRA_PERMS]:
                        asesor_perms.append(p)
                elif app_label in {"customers", "vehicles", "catalog", "workorders"}:
                    if code.startswith("view_"):
                        asesor_perms.append(p)
        asesor_group.permissions.set(asesor_perms)

        # 6) Mecánico = solo view de todo lo relevante
        mecanico_perms = [p for plist in perms_by_model.values() for p in plist if p.codename.startswith("view_")]
        mecanico_group.permissions.set(mecanico_perms)

        self.stdout.write(self.style.SUCCESS("✔ Admin: permisos asignados."))
        self.stdout.write(self.style.SUCCESS("✔ Asesor: permisos asignados."))
        self.stdout.write(self.style.SUCCESS("✔ Mecanico: permisos asignados."))
        self.stdout.write(self.style.SUCCESS("🎯 Roles creados/actualizados con éxito."))
