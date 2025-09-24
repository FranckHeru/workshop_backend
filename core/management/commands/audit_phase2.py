# core/management/commands/audit_phase2.py
from pathlib import Path
import json

from django.core.management.base import BaseCommand
from django.conf import settings
from django.urls import reverse, NoReverseMatch
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


OK = "[OK]"
WARN = "[WARN]"
ERR = "[ERR]"


class Command(BaseCommand):
    """
    Auditoría Fase 2:
    - Verifica apps clave (DRF, filtros, Spectacular, CORS, quotes).
    - Verifica rutas OpenAPI/Swagger/ReDoc y JWT.
    - Verifica permisos finos de quotes y su asignación a grupos Admin/Asesor.
    - Verifica acciones del QuotationViewSet.
    - Exporta el esquema OpenAPI a docs/Workshop_API_phase2.yaml
    - Genera MANIFEST_FASE2.txt con el resultado.
    """
    help = "Auditoría Fase 2: permisos finos, OpenAPI/Swagger y JWT."

    def handle(self, *args, **kwargs):
        base_dir: Path = Path(settings.BASE_DIR)
        docs_dir = base_dir / "docs"
        docs_dir.mkdir(exist_ok=True)

        out_lines: list[str] = []

        def log(line: str):
            self.stdout.write(line)
            out_lines.append(line)

        log("Fase 2 – Auditoría")
        log(f"Proyecto: {base_dir}")

        # === APPS / DRF / SPECTACULAR ===
        log("\n=== APPS / DRF / Swagger ===")

        def has_app(name: str) -> bool:
            """
            Detecta app por nombre corto (p.ej. 'quotes') o por AppConfig
            (p.ej. 'quotes.apps.QuotesConfig').
            """
            for entry in settings.INSTALLED_APPS:
                if entry == name:
                    return True
                # Si viene como 'quotes.apps.QuotesConfig', comparar el primer segmento
                if entry.endswith(".apps.QuotesConfig") and entry.split(".")[0] == name:
                    return True
            return False

        checks = [
            ("rest_framework", has_app("rest_framework")),
            ("django_filters", has_app("django_filters")),
            ("drf_spectacular", has_app("drf_spectacular")),
            ("corsheaders", has_app("corsheaders")),
            ("quotes", has_app("quotes")),
        ]
        for app, ok in checks:
            log(f"{OK if ok else ERR} {app} {'presente' if ok else 'faltante'}")

        # === URLS: schema / swagger / redoc / jwt ===
        log("\n=== RUTAS (OpenAPI/JWT) ===")

        def check_reverse(name: str, label: str) -> bool:
            try:
                url = reverse(name)
                log(f"{OK} {label}: {url}")
                return True
            except NoReverseMatch as e:
                log(f"{ERR} {label}: no encontrada ({e})")
                return False

        check_reverse("schema", "OpenAPI schema")
        check_reverse("swagger-ui", "Swagger UI")
        check_reverse("redoc", "ReDoc")

        # JWT puede estar namespaced; probamos nombres comunes
        jwt_ok = False
        for nm, label in [
            ("jwt-create", "JWT create"),
            ("jwt-refresh", "JWT refresh"),
            ("token_obtain_pair", "JWT obtain pair"),
            ("token_refresh", "JWT refresh (simplejwt)"),
        ]:
            try:
                url = reverse(nm)
                log(f"{OK} {label}: {url} (name={nm})")
                jwt_ok = True
            except NoReverseMatch:
                pass
        if not jwt_ok:
            log(f"{WARN} JWT: no se detectaron rutas por nombre (revisar include en core.urls)")

        # === PERMISOS FINOS (quotes.*) y GRUPOS ===
        log("\n=== PERMISOS FINOS (quotes) y grupos ===")
        wanted_perms = [
            ("send_quotation", "quotes.send_quotation"),
            ("approve_quotation", "quotes.approve_quotation"),
            ("reject_quotation", "quotes.reject_quotation"),
            ("convert_quotation_to_workorder", "quotes.convert_quotation_to_workorder"),
        ]
        try:
            ct_quotes = ContentType.objects.get(app_label="quotes", model="quotation")
        except ContentType.DoesNotExist:
            ct_quotes = None
            log(f"{ERR} ContentType quotes.Quotation no encontrado (¿migraciones aplicadas?)")

        for codename, full in wanted_perms:
            try:
                if ct_quotes:
                    Permission.objects.get(content_type=ct_quotes, codename=codename)
                else:
                    Permission.objects.get(codename=codename)
                log(f"{OK} perm {full}")
            except Permission.DoesNotExist:
                log(f"{ERR} perm {full} faltante")

        for grp_name in ["Admin", "Asesor"]:
            try:
                grp = Group.objects.get(name=grp_name)
                log(f"{OK} grupo {grp_name}")
                # Checar asignación de cada permiso fino
                for _, full in wanted_perms:
                    has = grp.permissions.filter(codename=full.split(".")[1]).exists()
                    log(f"{OK if has else ERR} {grp_name} ⇒ {full}")
            except Group.DoesNotExist:
                log(f"{ERR} grupo {grp_name} faltante")

        # === QUOTES: permisos por acción presentes ===
        log("\n=== QUOTES (ViewSet/Permisos por acción) ===")
        try:
            from quotes.views import QuotationViewSet  # tu API actual
            # Confirmar que tiene acciones clave
            for meth in ["approve", "reject", "send", "to_workorder"]:
                has = hasattr(QuotationViewSet, meth)
                log(f"{OK if has else ERR} ViewSet action .{meth}")
            # Mostrar permission_classes configuradas en la vista
            perm_names = [getattr(p, "__name__", str(p)) for p in getattr(QuotationViewSet, "permission_classes", [])]
            perm_blob = ", ".join(perm_names) or "(vacío)"
            log(f"{OK} permission_classes en QuotationViewSet: {perm_blob}")
        except Exception as e:
            log(f"{ERR} Import quotes.views.QuotationViewSet: {e}")

        # === Generar esquema OpenAPI a docs/ ===
        log("\n=== OpenAPI Schema (export) ===")
        schema_yaml_path = docs_dir / "Workshop_API_phase2.yaml"
        try:
            from drf_spectacular.generators import SchemaGenerator

            gen = SchemaGenerator()
            schema = gen.get_schema(request=None, public=True)

            # Intentamos YAML; si no hay PyYAML, exportamos JSON.
            try:
                import yaml  # type: ignore

                # Convertimos a tipos serializables básicos
                as_dict = json.loads(json.dumps(schema, default=str))
                with schema_yaml_path.open("w", encoding="utf-8") as fh:
                    yaml.safe_dump(as_dict, fh, sort_keys=False, allow_unicode=True)
                log(f"{OK} Schema YAML exportado: {schema_yaml_path}")
            except Exception:
                schema_json_path = docs_dir / "Workshop_API_phase2.json"
                with schema_json_path.open("w", encoding="utf-8") as fh:
                    json.dump(schema, fh, default=str, ensure_ascii=False, indent=2)
                log(f"{WARN} PyYAML no disponible: exportado JSON → {schema_json_path}")
        except Exception as e:
            log(f"{ERR} No se pudo generar schema: {e}")

        # === Guardar MANIFIESTO ===
        manifest = base_dir / "MANIFEST_FASE2.txt"
        manifest.write_text("\n".join(out_lines), encoding="utf-8")
        log(f"\n✔ Auditoría completada. Se generó: {manifest}")
