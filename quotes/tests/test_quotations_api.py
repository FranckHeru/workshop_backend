import pytest
from rest_framework import status
from customers.models import Customer
from vehicles.models import Vehicle
from catalog.models import Service, Part

@pytest.mark.django_db
class TestQuotationAPI:
    def _seed(self):
        customer = Customer.objects.create(name="Juan Pérez")
        vehicle = Vehicle.objects.create(owner=customer, plate="P123DEF")  # <- owner
        svc = Service.objects.create(name="Alineación", price=50)
        part = Part.objects.create(name="Filtro Aceite", price=20)
        return customer, vehicle, svc, part

    def test_create_quotation_with_items(self, auth_api):
        client, _ = auth_api("Asesor")
        customer, vehicle, svc, part = self._seed()

        payload = {
            "customer": customer.id,
            "vehicle": vehicle.id,
            "services": [{"service": svc.id, "quantity": 2, "unit_price": "50"}],
            "parts": [{"part": part.id, "quantity": 1, "unit_price": "20"}],
        }
        res = client.post("/api/quotations/", payload, format="json")
        assert res.status_code in (200, 201), res.data
        data = res.json()
        assert data.get("customer") == customer.id
        assert data.get("vehicle") == vehicle.id

    def test_business_flow_approve_convert(self, auth_api):
        client, _ = auth_api("Asesor")
        customer, vehicle, svc, _ = self._seed()

        res = client.post("/api/quotations/", {
            "customer": customer.id,
            "vehicle": vehicle.id,
            "services": [{"service": svc.id, "quantity": 1, "unit_price": "50"}],
            "parts": []
        }, format="json")
        assert res.status_code in (200, 201)
        qid = res.json()["id"]

        assert client.post(f"/api/quotations/{qid}/approve/", {}).status_code in (200, 201)
        r2 = client.post(f"/api/quotations/{qid}/to-workorder/", {})
        assert r2.status_code in (200, 201)
        assert "workorder_id" in r2.json()
