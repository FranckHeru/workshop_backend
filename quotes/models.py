from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q, F, CheckConstraint
from decimal import Decimal, ROUND_HALF_UP

# ----------------- Util redondeo -----------------
TWOPL = Decimal("0.01")

def q2(x) -> Decimal:
    if isinstance(x, Decimal):
        d = x
    else:
        d = Decimal(str(x))
    return d.quantize(TWOPL, rounding=ROUND_HALF_UP)


class Quotation(models.Model):
    DRAFT = "DRAFT"
    SENT = "SENT"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    STATUS_CHOICES = [
        (DRAFT, "Borrador"),
        (SENT, "Enviada"),
        (APPROVED, "Aprobada"),
        (REJECTED, "Rechazada"),
        (EXPIRED, "Vencida"),
    ]

    number = models.CharField("Número", max_length=20, unique=True)
    status = models.CharField("Estado", max_length=10, choices=STATUS_CHOICES, default=DRAFT)

    customer = models.ForeignKey(
        "customers.Customer", on_delete=models.PROTECT, related_name="quotations", verbose_name="Cliente"
    )
    vehicle = models.ForeignKey(
        "vehicles.Vehicle", on_delete=models.PROTECT, related_name="quotations", null=True, blank=True, verbose_name="Vehículo"
    )
    notes = models.TextField("Notas", blank=True)
    valid_until = models.DateField("Válida hasta", null=True, blank=True)

    subtotal_services = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    subtotal_parts = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["number"]), models.Index(fields=["status"])]
        constraints = [
            CheckConstraint(check=Q(subtotal_services__gte=0), name="q_subtot_services_gte_0"),
            CheckConstraint(check=Q(subtotal_parts__gte=0),   name="q_subtot_parts_gte_0"),
            CheckConstraint(check=Q(discount_total__gte=0),   name="q_discount_total_gte_0"),
            CheckConstraint(check=Q(tax_total__gte=0),        name="q_tax_total_gte_0"),
            CheckConstraint(check=Q(grand_total__gte=0),      name="q_grand_total_gte_0"),
        ]

    def __str__(self):
        return f"Quotation {self.number} ({self.get_status_display()})"

    # ---------- Workflow helpers ----------
    @classmethod
    def status_values(cls):
        return [c[0] for c in cls.STATUS_CHOICES]

    @classmethod
    def allowed_transitions(cls):
        choices = set(cls.status_values())
        default = {
            cls.DRAFT: {cls.SENT, cls.REJECTED},
            cls.SENT: {cls.APPROVED, cls.REJECTED},
            cls.APPROVED: set(),
            cls.REJECTED: set(),
            cls.EXPIRED: set(),
        }
        return {k: (v & choices) for k, v in default.items() if k in choices}

    def can_transition(self, to_status: str) -> bool:
        if to_status not in self.status_values():
            return False
        table = self.allowed_transitions()
        cur = getattr(self, "status", None)
        if cur not in table:
            return True
        return to_status in table[cur]

    # ---------- Validación negocio ----------
    def clean(self):
        if self.customer_id and self.vehicle_id:
            from vehicles.models import Vehicle
            veh_cust_id = (
                Vehicle.objects.only("customer_id")
                .filter(pk=self.vehicle_id)
                .values_list("customer_id", flat=True)
                .first()
            )
            if veh_cust_id and veh_cust_id != self.customer_id:
                raise ValidationError({"vehicle": "El vehículo no pertenece al cliente seleccionado."})

    # ---------- Persistencia / numeración ----------
    def save(self, *args, **kwargs):
        if not self.number:
            today = timezone.now().date()
            year = today.year
            prefix = f"Q-{year}-"
            last = Quotation.objects.filter(number__startswith=prefix).order_by("number").last()
            if last and last.number.split("-")[-1].isdigit():
                seq = int(last.number.split("-")[-1]) + 1
            else:
                seq = 1
            self.number = f"{prefix}{seq:04d}"

        # cuantiza totales “manuales” por si alguien los setea directo (admin/api)
        self.discount_total = q2(self.discount_total or 0)
        self.tax_total = q2(self.tax_total or 0)
        super().save(*args, **kwargs)

    # ---------- Totales ----------
    def recalc_totals(self):
        s_sum = Decimal("0.00")
        p_sum = Decimal("0.00")
        for i in self.services.all():
            s_sum += (i.quantity * i.unit_price) - i.discount
        for i in self.parts.all():
            p_sum += (i.quantity * i.unit_price) - i.discount

        s_sum = q2(max(s_sum, Decimal("0.00")))
        p_sum = q2(max(p_sum, Decimal("0.00")))
        d_tot = q2(max(self.discount_total or 0, Decimal("0.00")))
        t_tot = q2(max(self.tax_total or 0, Decimal("0.00")))

        g_tot = q2(max(s_sum + p_sum - d_tot + t_tot, Decimal("0.00")))

        self.subtotal_services = s_sum
        self.subtotal_parts = p_sum
        self.discount_total = d_tot
        self.tax_total = t_tot
        self.grand_total = g_tot

        super().save(update_fields=[
            "subtotal_services", "subtotal_parts", "discount_total", "tax_total", "grand_total", "updated_at"
        ])


class QuotationService(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name="services")
    service = models.ForeignKey("catalog.Service", on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("1.00"))
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        constraints = [
            CheckConstraint(check=Q(quantity__gt=0), name="qs_quantity_gt_0"),
            CheckConstraint(check=Q(unit_price__gte=0), name="qs_unit_price_gte_0"),
            CheckConstraint(check=Q(discount__gte=0), name="qs_discount_gte_0"),
            CheckConstraint(check=Q(discount__lte=F("quantity") * F("unit_price")), name="qs_discount_le_subtotal"),
        ]

    def __str__(self):
        return f"{self.service} x {self.quantity}"

    @property
    def line_total(self) -> Decimal:
        return q2((self.quantity * self.unit_price) - self.discount)

    def clean(self):
        if self.quantity is None or self.quantity <= 0:
            raise ValidationError({"quantity": "Debe ser > 0"})
        if self.unit_price is None or self.unit_price < 0:
            raise ValidationError({"unit_price": "Debe ser ≥ 0"})
        if self.discount is None or self.discount < 0:
            raise ValidationError({"discount": "Debe ser ≥ 0"})
        if self.discount > (self.quantity * self.unit_price):
            raise ValidationError({"discount": "No puede exceder el subtotal (cantidad × precio)."})

    def save(self, *args, **kwargs):
        # cuantiza antes de guardar
        self.quantity = q2(self.quantity or 0)
        self.unit_price = q2(self.unit_price or 0)
        self.discount = q2(self.discount or 0)
        super().save(*args, **kwargs)
        try:
            if self.quotation_id:
                self.quotation.recalc_totals()
        except Exception:
            pass

    def delete(self, *args, **kwargs):
        q = self.quotation
        super().delete(*args, **kwargs)
        try:
            if q:
                q.recalc_totals()
        except Exception:
            pass


class QuotationPart(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name="parts")
    part = models.ForeignKey("catalog.Part", on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("1.00"))
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        constraints = [
            CheckConstraint(check=Q(quantity__gt=0), name="qp_quantity_gt_0"),
            CheckConstraint(check=Q(unit_price__gte=0), name="qp_unit_price_gte_0"),
            CheckConstraint(check=Q(discount__gte=0), name="qp_discount_gte_0"),
            CheckConstraint(check=Q(discount__lte=F("quantity") * F("unit_price")), name="qp_discount_le_subtotal"),
        ]

    def __str__(self):
        return f"{self.part} x {self.quantity}"

    @property
    def line_total(self) -> Decimal:
        return q2((self.quantity * self.unit_price) - self.discount)

    def clean(self):
        if self.quantity is None or self.quantity <= 0:
            raise ValidationError({"quantity": "Debe ser > 0"})
        if self.unit_price is None or self.unit_price < 0:
            raise ValidationError({"unit_price": "Debe ser ≥ 0"})
        if self.discount is None or self.discount < 0:
            raise ValidationError({"discount": "Debe ser ≥ 0"})
        if self.discount > (self.quantity * self.unit_price):
            raise ValidationError({"discount": "No puede exceder el subtotal (cantidad × precio)."})

    def save(self, *args, **kwargs):
        self.quantity = q2(self.quantity or 0)
        self.unit_price = q2(self.unit_price or 0)
        self.discount = q2(self.discount or 0)
        super().save(*args, **kwargs)
        try:
            if self.quotation_id:
                self.quotation.recalc_totals()
        except Exception:
            pass

    def delete(self, *args, **kwargs):
        q = self.quotation
        super().delete(*args, **kwargs)
        try:
            if q:
                q.recalc_totals()
        except Exception:
            pass
