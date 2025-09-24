from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable, Tuple

from django.db import transaction
from rest_framework import serializers

from .models import Quotation, QuotationService, QuotationPart


# -------- utilidades de decimales / totales --------

def q2(v) -> Decimal:
    """Convierte a Decimal con 2 decimales (ROUND_HALF_UP)."""
    d = Decimal(v or 0)
    return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def compute_line_total(quantity: Decimal, unit_price: Decimal, discount: Decimal) -> Decimal:
    """
    Descuento híbrido:
      - discount <= 1   -> porcentaje (0.10 = 10%)
      - discount  > 1   -> monto por unidad (p.ej. 15.00)
    """
    quantity = Decimal(quantity or 0)
    unit_price = Decimal(unit_price or 0)
    discount = Decimal(discount or 0)

    if discount <= 1:
        effective = unit_price * (Decimal("1") - discount)
    else:
        effective = unit_price - discount
    if effective < 0:
        effective = Decimal("0")
    return q2(quantity * effective)


# -------- serializers de renglones --------

class QuotationServiceSerializer(serializers.ModelSerializer):
    line_total = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = QuotationService
        fields = ["id", "service", "quantity", "unit_price", "discount", "line_total"]

    def validate(self, data):
        if (data.get("quantity", 0) or 0) < 0:
            raise serializers.ValidationError({"quantity": "Debe ser >= 0"})
        if (data.get("unit_price", 0) or 0) < 0:
            raise serializers.ValidationError({"unit_price": "Debe ser >= 0"})
        if (data.get("discount", 0) or 0) < 0:
            raise serializers.ValidationError({"discount": "Debe ser >= 0"})
        return data

    # ← Type hint para Spectacular
    def get_line_total(self, obj) -> str:
        return str(compute_line_total(obj.quantity, obj.unit_price, obj.discount))


class QuotationPartSerializer(serializers.ModelSerializer):
    line_total = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = QuotationPart
        fields = ["id", "part", "quantity", "unit_price", "discount", "line_total"]

    def validate(self, data):
        if (data.get("quantity", 0) or 0) < 0:
            raise serializers.ValidationError({"quantity": "Debe ser >= 0"})
        if (data.get("unit_price", 0) or 0) < 0:
            raise serializers.ValidationError({"unit_price": "Debe ser >= 0"})
        if (data.get("discount", 0) or 0) < 0:
            raise serializers.ValidationError({"discount": "Debe ser >= 0"})
        return data

    # ← Type hint para Spectacular
    def get_line_total(self, obj) -> str:
        return str(compute_line_total(obj.quantity, obj.unit_price, obj.discount))


# -------- serializer de cabecera (Quotation) --------

class QuotationSerializer(serializers.ModelSerializer):
    # nested write + lectura enriquecida
    services = QuotationServiceSerializer(many=True, required=False)
    parts = QuotationPartSerializer(many=True, required=False)

    # totales listos para frontend (como strings)
    subtotal_services = serializers.SerializerMethodField()
    subtotal_parts = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = Quotation
        fields = "__all__"  # incluye campos del modelo + los de arriba
        read_only_fields = ["created_at", "updated_at"]

    # -------- validaciones de cabecera --------
    def validate(self, data):
        """
        - El vehículo (si viene) debe pertenecer al cliente.
        (se valida también en el modelo; aquí lo reflejamos para respuesta 400 temprana)
        """
        customer = data.get("customer") or getattr(self.instance, "customer", None)
        vehicle = data.get("vehicle") or getattr(self.instance, "vehicle", None)
        if customer and vehicle:
            try:
                from vehicles.models import Vehicle
                veh_cust_id = (
                    Vehicle.objects.only("customer_id")
                    .filter(pk=vehicle.pk)
                    .values_list("customer_id", flat=True)
                    .first()
                )
                if veh_cust_id and veh_cust_id != customer.pk:
                    raise serializers.ValidationError(
                        {"vehicle": "El vehículo no pertenece al cliente seleccionado."}
                    )
            except Exception:
                # Cualquier error de import/consulta lo dejamos pasar para que lo capture la validación del modelo
                pass
        return data

    # -------- helpers internos --------
    def _split_items(self, items: Iterable[dict]) -> Tuple[list, list]:
        """Separa items con id (actualizar) y sin id (crear)."""
        to_update, to_create = [], []
        for item in items or []:
            (to_update if item.get("id") else to_create).append(item)
        return to_update, to_create

    def _upsert_children(self, instance: Quotation, services, parts):
        # SERVICES
        if services is not None:
            to_update, to_create = self._split_items(services)
            keep_ids = set()

            # actualizar existentes por id
            for data in to_update:
                obj = instance.services.filter(pk=data["id"]).first()
                if not obj:
                    continue
                for f in ["service", "quantity", "unit_price", "discount"]:
                    if f in data:
                        setattr(obj, f, data[f])
                obj.save()
                keep_ids.add(obj.id)

            # crear nuevos
            for data in to_create:
                obj = QuotationService.objects.create(quotation=instance, **data)
                keep_ids.add(obj.id)

            # eliminar los que ya no vienen
            instance.services.exclude(pk__in=keep_ids).delete()

        # PARTS
        if parts is not None:
            to_update, to_create = self._split_items(parts)
            keep_ids = set()

            for data in to_update:
                obj = instance.parts.filter(pk=data["id"]).first()
                if not obj:
                    continue
                for f in ["part", "quantity", "unit_price", "discount"]:
                    if f in data:
                        setattr(obj, f, data[f])
                obj.save()
                keep_ids.add(obj.id)

            for data in to_create:
                obj = QuotationPart.objects.create(quotation=instance, **data)
                keep_ids.add(obj.id)

            instance.parts.exclude(pk__in=keep_ids).delete()

    # -------- create/update --------
    @transaction.atomic
    def create(self, validated_data):
        services = validated_data.pop("services", [])
        parts = validated_data.pop("parts", [])

        # Crear cabecera
        quotation = Quotation(**validated_data)
        # Ejecuta validaciones del modelo (clean)
        try:
            quotation.full_clean(exclude=None)
        except Exception as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, "message_dict") else str(e))
        quotation.save()

        # Crear renglones
        for item in services:
            QuotationService.objects.create(quotation=quotation, **item)
        for item in parts:
            QuotationPart.objects.create(quotation=quotation, **item)

        # Recalcular totales (persistidos en el modelo)
        if hasattr(quotation, "recalc_totals"):
            quotation.recalc_totals()
        return quotation

    @transaction.atomic
    def update(self, instance, validated_data):
        services = validated_data.pop("services", None)
        parts = validated_data.pop("parts", None)

        # Actualiza cabecera
        for k, v in validated_data.items():
            setattr(instance, k, v)

        # Validaciones del modelo antes de guardar
        try:
            instance.full_clean(exclude=None)
        except Exception as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, "message_dict") else str(e))

        instance.save()

        # Upsert renglones (solo si vienen en el payload)
        self._upsert_children(instance, services, parts)

        # Totales
        if hasattr(instance, "recalc_totals"):
            instance.recalc_totals()
        return instance

    # -------- totales para frontend (strings) --------
    def _sum_queryset(self, qs) -> Decimal:
        total = Decimal("0")
        for obj in qs:
            total += compute_line_total(obj.quantity, obj.unit_price, obj.discount)
        return q2(total)

    # ← Type hints para Spectacular
    def get_subtotal_services(self, obj) -> str:
        # usa related_name 'services'
        return str(self._sum_queryset(obj.services.all()))

    def get_subtotal_parts(self, obj) -> str:
        return str(self._sum_queryset(obj.parts.all()))

    def get_total(self, obj) -> str:
        """
        Total para UI = subtotal_services + subtotal_parts - discount_total + tax_total
        (Mantenemos en sync con el cálculo del modelo.)
        """
        s = Decimal(self.get_subtotal_services(obj))
        p = Decimal(self.get_subtotal_parts(obj))
        disc = Decimal(obj.discount_total or 0)
        tax = Decimal(obj.tax_total or 0)
        return str(q2(s + p - disc + tax))
