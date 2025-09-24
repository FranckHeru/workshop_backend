import pytest
from rest_framework import status
from customers.models import Customer
from vehicles.models import Vehicle
from catalog.models import Service
from quotes.models import Quotation, QuotationService

def _mk_quotation_basic():
    c = Customer.objects.create(name="Juan Pérez")
    v = Vehicle.objects.create(owner=c, plate="P123ABC")  # <- owner requerido
    q = Quotation.objects.create(customer=c, vehicle=v)
    s = Service.objects.create(name="Diagnóstico", price=100)
    QuotationService.objects.create(quotation=q, service=s, quantity=1, unit_price=100)
    return q

@pytest.mark.django_db
def test_perm_aprobar_cotizacion_restringido(auth_api):
    q = _mk_quotation_basic()

    # Mecanico -> 403
    client_mech, _ = auth_api("Mecanico")
    r_forbid = client_mech.post(f"/api/quotations/{q.id}/approve/", {})
    assert r_forbid.status_code == status.HTTP_403_FORBIDDEN

    # Asesor -> OK
    client_ok, _ = auth_api("Asesor")
    r_ok = client_ok.post(f"/api/quotations/{q.id}/approve/", {})
    assert r_ok.status_code in (200, 201)
    assert r_ok.json().get("status") == getattr(Quotation, "APPROVED", "APPROVED")

@pytest.mark.django_db
def test_perm_reject_send_convert(auth_api):
    q = _mk_quotation_basic()
    client, _ = auth_api("Asesor")

    assert client.post(f"/api/quotations/{q.id}/send/", {}).status_code in (200, 201)
    assert client.post(f"/api/quotations/{q.id}/reject/", {}).status_code in (200, 201)
    assert client.post(f"/api/quotations/{q.id}/approve/", {}).status_code in (200, 201)

    r_conv = client.post(f"/api/quotations/{q.id}/to-workorder/", {})
    assert r_conv.status_code in (200, 201)
    assert "workorder_id" in r_conv.json()
