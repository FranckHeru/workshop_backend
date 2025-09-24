from django.db import transaction
from django.utils.timezone import now

from rest_framework import status, permissions, filters
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from .models import Quotation
from .serializers import QuotationSerializer

# ────────────────────────────────────────────────────────────────────────────────
# Permisos: rol general + permisos finos por acción
# ────────────────────────────────────────────────────────────────────────────────
try:
    # Regla de rol del proyecto: sólo Admin/Asesor pueden escribir (o staff/superuser)
    from core.permissions import (
        WriteRequiresAdminOrAsesor as WriteRolePerm,
        CanSendQuotation,
        CanApproveQuotation,
        CanRejectQuotation,
        CanConvertQuotation,
    )
except Exception:
    # Fallbacks seguros si aún no tienes core.permissions
    WriteRolePerm = permissions.IsAuthenticated

    class _Allow(permissions.BasePermission):
        def has_permission(self, request, view):
            return bool(request.user and request.user.is_authenticated)

    CanSendQuotation = CanApproveQuotation = CanRejectQuotation = CanConvertQuotation = _Allow


# ────────────────────────────────────────────────────────────────────────────────
# Utilidades internas
# ────────────────────────────────────────────────────────────────────────────────
def _const(model, name: str, default: str) -> str:
    """Devuelve constante del modelo si existe; de lo contrario, string por defecto."""
    return getattr(model, name, default)


def _allowed_statuses_from_choices(model) -> set:
    """Intenta leer las choices del campo status; si no hay, devuelve set vacío."""
    try:
        field = model._meta.get_field("status")
        if getattr(field, "choices", None):
            return {c[0] for c in field.choices}
    except Exception:
        pass
    return set()


# ────────────────────────────────────────────────────────────────────────────────
# Vista principal
# ────────────────────────────────────────────────────────────────────────────────
class QuotationViewSet(ModelViewSet):
    """
    API para Cotizaciones, con filtros/búsquedas/orden y acciones de negocio.
    """
    queryset = (
        Quotation.objects
        .select_related("customer", "vehicle")
        .prefetch_related("services", "parts")
        .all()
    )
    serializer_class = QuotationSerializer

    # Cinturón general: autenticado + rol (Admin/Asesor) para operaciones CRUD
    permission_classes = [permissions.IsAuthenticated & WriteRolePerm]

    # Filtrado y UX para frontend
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "customer", "vehicle", "created_at"]
    search_fields = ["number", "customer__name", "vehicle__plate"]
    ordering_fields = ["created_at", "updated_at", "number", "status"]
    ordering = ["-created_at"]

    # ────────────────────────────────────────────────────────────────────────
    # Acciones de estado (cada una con su permiso fino específico)
    # ────────────────────────────────────────────────────────────────────────

    @action(
        detail=True, methods=["post"],
        permission_classes=[permissions.IsAuthenticated, WriteRolePerm, CanApproveQuotation],
    )
    def approve(self, request, pk=None):
        """
        Pone la cotización en estado APPROVED.
        Requiere permiso: quotes.approve_quotation
        """
        q = self.get_object()
        approved_value = _const(Quotation, "APPROVED", "APPROVED")

        # Validar contra choices si existen
        choices = _allowed_statuses_from_choices(Quotation)
        if choices and approved_value not in choices:
            return Response(
                {"detail": f"Estado '{approved_value}' no permitido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        q.status = approved_value
        if hasattr(q, "approved_at"):
            q.approved_at = now()
        q.save(update_fields=["status"] + (["approved_at"] if hasattr(q, "approved_at") else []))
        return Response({"id": q.id, "number": q.number, "status": q.status})

    @action(
        detail=True, methods=["post"],
        permission_classes=[permissions.IsAuthenticated, WriteRolePerm, CanRejectQuotation],
    )
    def reject(self, request, pk=None):
        """
        Pone la cotización en estado REJECTED.
        Requiere permiso: quotes.reject_quotation
        """
        q = self.get_object()
        rejected_value = _const(Quotation, "REJECTED", "REJECTED")

        choices = _allowed_statuses_from_choices(Quotation)
        if choices and rejected_value not in choices:
            return Response(
                {"detail": f"Estado '{rejected_value}' no permitido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        q.status = rejected_value
        if hasattr(q, "rejected_at"):
            q.rejected_at = now()
        q.save(update_fields=["status"] + (["rejected_at"] if hasattr(q, "rejected_at") else []))
        return Response({"id": q.id, "number": q.number, "status": q.status})

    @action(
        detail=True, methods=["post"],
        permission_classes=[permissions.IsAuthenticated, WriteRolePerm, CanSendQuotation],
    )
    def send(self, request, pk=None):
        """
        Pone la cotización en estado SENT (enviada al cliente).
        Requiere permiso: quotes.send_quotation
        """
        q = self.get_object()
        sent_value = _const(Quotation, "SENT", "SENT")

        choices = _allowed_statuses_from_choices(Quotation)
        if choices and sent_value not in choices:
            return Response(
                {"detail": f"Estado '{sent_value}' no permitido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        q.status = sent_value
        if hasattr(q, "sent_at"):
            q.sent_at = now()
        q.save(update_fields=["status"] + (["sent_at"] if hasattr(q, "sent_at") else []))
        return Response({"id": q.id, "number": q.number, "status": q.status})

    @action(detail=True, methods=["post"])
    def set_status(self, request, pk=None):
        """
        Cambia el estado a un valor arbitrario recibido en el body:
        { "status": "<nuevo_estado>" }
        - Si el modelo tiene choices, se valida contra esas choices.
        (Este endpoint en general se protege con permisos de cambio del modelo)
        """
        q = self.get_object()
        new_status = (request.data or {}).get("status")
        if not new_status:
            return Response({"detail": "Falta 'status'."}, status=status.HTTP_400_BAD_REQUEST)

        choices = _allowed_statuses_from_choices(Quotation)
        if choices and new_status not in choices:
            return Response(
                {"detail": f"Estado '{new_status}' no permitido. Options: {sorted(choices)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        q.status = new_status
        q.save(update_fields=["status"])
        return Response({"id": q.id, "number": q.number, "status": q.status})

    # ────────────────────────────────────────────────────────────────────────
    # Generar Orden de Trabajo desde la cotización
    # ────────────────────────────────────────────────────────────────────────
    @action(
        detail=True, methods=["post"], url_path="to-workorder",
        permission_classes=[permissions.IsAuthenticated, WriteRolePerm, CanConvertQuotation],
    )
    @transaction.atomic
    def to_workorder(self, request, pk=None):
        """
        Crea una WorkOrder a partir de la cotización APROBADA.
        Copia líneas y precios 1:1. Requiere apps: workorders, catalog.
        Requiere permiso: quotes.convert_quotation_to_workorder
        """
        q = self.get_object()
        approved_value = _const(Quotation, "APPROVED", "APPROVED")
        if q.status != approved_value:
            return Response(
                {"detail": f"La cotización debe estar en estado {approved_value}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Import tardío para evitar ciclos
        from workorders.models import WorkOrder, WorkOrderService, WorkOrderPart

        wo_status_open = _const(WorkOrder, "OPEN", "OPEN")
        wo = WorkOrder.objects.create(
            customer=q.customer,
            vehicle=q.vehicle,
            notes=f"Generada desde cotización {q.number}",
            status=wo_status_open,
        )

        # Copiar servicios/partes
        for s in q.services.all():
            WorkOrderService.objects.create(
                workorder=wo,
                service=s.service,
                quantity=s.quantity,
                unit_price=s.unit_price,
                discount=s.discount,
            )
        for p in q.parts.all():
            WorkOrderPart.objects.create(
                workorder=wo,
                part=p.part,
                quantity=p.quantity,
                unit_price=p.unit_price,
                discount=p.discount,
            )

        if hasattr(wo, "recalc_totals"):
            wo.recalc_totals()

        return Response({"workorder_id": wo.id, "from_quotation": q.number}, status=status.HTTP_201_CREATED)
