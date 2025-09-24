from django.db import models
from customers.models import Customer
from vehicles.models import Vehicle
from catalog.models import Service, Part

class WorkOrder(models.Model):
    OPEN = 'OPEN'
    IN_PROGRESS = 'IN_PROGRESS'
    DONE = 'DONE'
    CANCELLED = 'CANCELLED'
    STATUS_CHOICES = [
        (OPEN, 'Abierta'),
        (IN_PROGRESS, 'En proceso'),
        (DONE, 'Finalizada'),
        (CANCELLED, 'Cancelada'),
    ]

    number = models.CharField(max_length=20, unique=True)   # ejemplo: OT-000001
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='workorders')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='workorders')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=OPEN)
    complaint = models.TextField(blank=True, null=True)   # lo que reporta el cliente
    diagnosis = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'work_order'
        ordering = ['-opened_at']

    def __str__(self):
        return self.number

class WorkOrderService(models.Model):
    workorder = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='services')
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'work_order_service'

class WorkOrderPart(models.Model):
    workorder = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='parts')
    part = models.ForeignKey(Part, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'work_order_part'
