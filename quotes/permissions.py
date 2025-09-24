# quotes/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

# Mapa de acción -> permiso requerido
ACTION_PERMS = {
    "approve":      "quotes.approve_quotation",
    "reject":       "quotes.reject_quotation",
    "send":         "quotes.send_quotation",
    "to_workorder": "quotes.convert_quotation_to_workorder",
    # opcional: fuerza permiso de cambio para set_status
    "set_status":   "quotes.change_quotation",
}

class QuotationActionPermissions(BasePermission):
    """
    - Lectura: permitida a autenticados (la combina tu WriteRolePerm).
    - Acciones custom: requieren permisos finos definidos arriba.
    - Para métodos "normales" (create/update/delete), dejamos que los
      otros permisos/roles del proyecto decidan (WriteRolePerm / DjangoModelPermissions).
    """
    def has_permission(self, request, view):
        # SAFE_METHODS (GET/HEAD/OPTIONS) no requieren permiso fino aquí
        if request.method in SAFE_METHODS:
            return True

        action = getattr(view, "action", None)
        if action in ACTION_PERMS:
            return bool(request.user and request.user.is_authenticated
                        and request.user.has_perm(ACTION_PERMS[action]))
        return True  # no es acción fina; delega a otros permisos de la vista

    def has_object_permission(self, request, view, obj):
        # Igual lógica a nivel objeto (por si quieres afinar luego)
        if request.method in SAFE_METHODS:
            return True
        action = getattr(view, "action", None)
        if action in ACTION_PERMS:
            return bool(request.user and request.user.is_authenticated
                        and request.user.has_perm(ACTION_PERMS[action]))
        return True
