# core/management/commands/audit_phase1.py
from __future__ import annotations
import os
from pathlib import Path
from typing import List

from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import Permission, Group
from django.apps import apps as dj_apps  # ← usar API oficial para detectar apps instaladas

OK = "OK"
WARN = "WARN"
FAIL = "FAIL"


def header(t: str) -> str:
    return f"\n=== {t} ==="


def line(status: str, msg: str) -> str:
    return f"[{status}] {msg}"


def exists_static(rel: str) -> bool:
    """
    Comprueba que el archivo estático (ruta relativa a /static, p.ej. 'img/login_bg.png')
    exista en alguna de las carpetas de STATICFILES_DIRS (o STATIC_ROOT).
    Evita usar os.sep directamente; construimos la ruta de forma portable.
    """
    # Construye la ruta relativa de forma OS-agnóstica
    rel_path = Path(*rel.split("/"))

    # Puede venir como strings o Paths
    dirs = getattr(settings, "STATICFILES_DIRS", []) or []
    for d in dirs:
        p = Path(d) / rel_path
        if p.exists():
            return True

    # Fallback: STATIC_ROOT si existiera
    sr = getattr(settings, "STATIC_ROOT", None)
    if sr:
        if (Path(sr) / rel_path).exists():
            return True

    return False


def check_installed_apps() -> List[str]:
    """
    Usa django.apps.apps.is_installed para soportar entradas como
    'app.apps.AppConfig' o etiquetas alternativas.
    """
    out = [header("INSTALLED_APPS")]
    required_any = [
        "jazzmin",
        "rest_framework",
        "django_filters",
        "core",
        "customers",
        "vehicles",
        "catalog",
        "quotes",
        "workorders",
    ]
    for app in required_any:
        ok = dj_apps.is_installed(app)
        out.append(line(OK if ok else WARN, f"{app} {'presente' if ok else 'no encontrado'}"))
    return out


def check_static_and_jazzmin() -> List[str]:
    out = [header("STATIC & JAZZMIN")]

    # STATICFILES_DIRS
    sdirs = getattr(settings, "STATICFILES_DIRS", []) or []
    out.append(line(OK if sdirs else WARN, f"STATICFILES_DIRS = {list(map(str, sdirs)) or '[]'}"))

    # Archivos de login y overrides
    for rel in ["img/login_logo.png", "img/login_bg.png", "css/admin_overrides.css", "js/admin_overrides.js"]:
        out.append(line(OK if exists_static(rel) else FAIL, f"/static/{rel}"))

    # JAZZMIN settings
    jset = getattr(settings, "JAZZMIN_SETTINGS", {}) or {}
    ccss = jset.get("custom_css")
    cjs = jset.get("custom_js", [])
    cjs_list = [cjs] if isinstance(cjs, str) else list(cjs or [])
    out.append(line(OK if ccss else WARN, f"JAZZMIN_SETTINGS.custom_css = {ccss!r}"))
    out.append(line(OK if cjs_list else WARN, f"JAZZMIN_SETTINGS.custom_js = {cjs_list!r}"))

    # Verificar que selector_extras.js esté referenciado y exista
    need = "js/selector_extras.js"
    has_selector = any(need == s or need in str(s) for s in cjs_list)
    out.append(line(OK if has_selector else WARN, f"Incluye {need} en custom_js"))
    if has_selector:
        out.append(line(OK if exists_static(need) else FAIL, f"/static/{need}"))

    # X_FRAME_OPTIONS
    xfo = getattr(settings, "X_FRAME_OPTIONS", None)
    out.append(line(OK if xfo in (None, "SAMEORIGIN") else WARN, f"X_FRAME_OPTIONS = {xfo!r}"))

    return out


def check_permissions_and_groups() -> List[str]:
    out = [header("PERMISOS Y GRUPOS")]
    needed = [
        ("quotes", "send_quotation"),
        ("quotes", "approve_quotation"),
        ("quotes", "reject_quotation"),
        ("quotes", "convert_quotation_to_workorder"),
    ]

    # Permisos
    for app_label, codename in needed:
        try:
            Permission.objects.get(content_type__app_label=app_label, codename=codename)
            out.append(line(OK, f"perm {app_label}.{codename}"))
        except Permission.DoesNotExist:
            out.append(line(FAIL, f"perm {app_label}.{codename} NO existe"))

    # Grupos mínimos
    groups = {}
    for gname in ("Admin", "Asesor", "Mecanico"):
        g, _ = Group.objects.get_or_create(name=gname)
        groups[gname] = g
        out.append(line(OK, f"grupo {gname}"))

    # Asignación esperada (comprobación suave)
    def has_perm(g: Group, app_label: str, codename: str) -> bool:
        return g.permissions.filter(content_type__app_label=app_label, codename=codename).exists()

    for gname in ("Admin", "Asesor"):
        g = groups[gname]
        for app_label, codename in needed:
            out.append(line(OK if has_perm(g, app_label, codename) else WARN, f"{gname} ⇒ {app_label}.{codename}"))
    return out


def check_quotes_models_and_routes() -> List[str]:
    out = [header("QUOTES (modelo/acciones)")]
    try:
        from quotes.models import Quotation
        out.append(line(OK, "quotes.models.Quotation import OK"))
        fields = {f.name for f in Quotation._meta.get_fields()}
        for fname in ("number", "status", "created_at", "updated_at"):
            out.append(line(OK if fname in fields else FAIL, f"Quotation.{fname}"))
        out.append(line(OK if hasattr(Quotation, "recalc_totals") else FAIL, "Quotation.recalc_totals()"))
        out.append(line(OK if hasattr(Quotation, "STATUS_CHOICES") else WARN, "STATUS_CHOICES"))
    except Exception as e:
        out.append(line(FAIL, f"No se pudo importar Quotation: {e}"))
        return out

    try:
        from quotes.views import QuotationViewSet
        out.append(line(OK, "quotes.views.QuotationViewSet import OK"))
        for meth in ("approve", "reject", "send", "to_workorder"):
            out.append(line(OK if hasattr(QuotationViewSet, meth) else FAIL, f"ViewSet action .{meth}"))
    except Exception as e:
        out.append(line(FAIL, f"No se pudo importar QuotationViewSet: {e}"))

    return out


class Command(BaseCommand):
    help = "Audita la Fase 1 del backend y genera MANIFEST_FASE1.txt con el resultado."

    def handle(self, *args, **options):
        report: List[str] = []
        report += [f"Fase 1 – Auditoría rápida\nProyecto: {getattr(settings, 'BASE_DIR', '?')}"]
        report += check_installed_apps()
        report += check_static_and_jazzmin()
        report += check_permissions_and_groups()
        report += check_quotes_models_and_routes()

        base_dir = Path(getattr(settings, "BASE_DIR", "."))
        out_path = base_dir / "MANIFEST_FASE1.txt"
        out_path.write_text("\n".join(report), encoding="utf-8")

        self.stdout.write(self.style.SUCCESS(f"✔ Auditoría completada. Se generó: {out_path}"))
        self.stdout.write("\n".join(report))
