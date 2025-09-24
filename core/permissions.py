# core/permissions.py
from typing import Iterable
from rest_framework import permissions

ALLOWED_WRITE_GROUPS = {"Admin", "Asesor"}

def _user_in_any_group(user, groups: Iterable[str]) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    try:
        user_groups = set(user.groups.values_list("name", flat=True))
    except Exception:
        return False
    return bool(user_groups & set(groups))

class ReadOnlyIfAuthenticated(permissions.BasePermission):
    """Sólo lectura para usuarios autenticados."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.method in permissions.SAFE_METHODS
        )

class WriteRequiresAdminOrAsesor(permissions.BasePermission):
    """Lectura para autenticados; escritura sólo Admin/Asesor (o staff/superuser)."""
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return _user_in_any_group(user, ALLOWED_WRITE_GROUPS)

# ---- Permisos finos Django (codenames) ----
class HasDjangoPermission(permissions.BasePermission):
    """Base: exige un permiso Django concreto (app_label.codename)."""
    perm_codename: str | None = None
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        if not self.perm_codename:
            return True
        return user.has_perm(self.perm_codename)

class CanSendQuotation(HasDjangoPermission):
    perm_codename = "quotes.send_quotation"

class CanApproveQuotation(HasDjangoPermission):
    perm_codename = "quotes.approve_quotation"

class CanRejectQuotation(HasDjangoPermission):
    perm_codename = "quotes.reject_quotation"

class CanConvertQuotation(HasDjangoPermission):
    perm_codename = "quotes.convert_quotation_to_workorder"
