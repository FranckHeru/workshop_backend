# core/tests/test_rbac_api.py
from django.contrib.auth.models import User, Group
from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient


def jwt_headers(username: str, password: str) -> dict:
    """
    Login contra /api/auth/jwt/create/ y devuelve headers Authorization Bearer.
    Lanza AssertionError si el login falla.
    """
    c = APIClient()
    res = c.post("/api/auth/jwt/create/", {"username": username, "password": password}, format="json")
    assert res.status_code == 200, f"Login falló para {username}: {res.status_code} {res.content!r}"
    access = res.data["access"]
    return {"HTTP_AUTHORIZATION": f"Bearer {access}"}


class RBACMinimalTests(TestCase):
    """
    Verifica permisos básicos por rol (Admin, Asesor, Mecanico) sobre endpoints CRUD.
    Depende de los grupos/permisos creados por el comando seed_roles.
    Cada test crea sus propios datos (no se comparten IDs entre tests).
    """

    @classmethod
    def setUpTestData(cls):
        # Asegura grupos/permisos tal como los definiste en el management command.
        call_command("seed_roles")

        # Usuarios para cada rol (idempotente con --keepdb)
        cls.admin, _ = User.objects.get_or_create(username="admin_test")
        cls.admin.set_password("admin123")
        cls.admin.save()

        cls.asesor, _ = User.objects.get_or_create(username="asesor_test")
        cls.asesor.set_password("asesor123")
        cls.asesor.save()

        cls.mecanico, _ = User.objects.get_or_create(username="mecanico_test")
        cls.mecanico.set_password("mecanico123")
        cls.mecanico.save()

        # Asignar grupos según nombres del seed
        Group.objects.get(name="Admin").user_set.add(cls.admin)
        Group.objects.get(name="Asesor").user_set.add(cls.asesor)
        Group.objects.get(name="Mecanico").user_set.add(cls.mecanico)

        # Cliente DRF reutilizable
        cls.client = APIClient()

    # ----------------- Helpers de datos por test -----------------

    def _create_customer(self, name="Juan Perez"):
        body = {
            "type": "PERSON",
            "name": name,
            "document_id": "0601-123456-001-1",
            "email": "juan.perez@example.com",
            "phone": "7777-8888",
            "address": "Calle 1",
            "is_active": True,
        }
        res = self.client.post("/api/customers/", body, format="json",
                               **jwt_headers("asesor_test", "asesor123"))
        self.assertEqual(res.status_code, 201, res.content)
        return res.data["id"], res.data

    def _create_vehicle(self, owner_id, plate="P123-456", brand="Toyota",
                        model="Corolla", year=2018, mileage_km=85000,
                        vin="1HGBH41JXMN109186", color="Azul"):
        vehicle = {
            "plate": plate,
            "vin": vin,
            "brand": brand,
            "model": model,
            "year": year,
            "color": color,
            "mileage_km": mileage_km,
            "owner": owner_id,
        }
        res = self.client.post("/api/vehicles/", vehicle, format="json",
                               **jwt_headers("asesor_test", "asesor123"))
        self.assertEqual(res.status_code, 201, res.content)
        return res.data["id"], res.data

    # ----------------- Clientes -----------------

    def test_customers_list_requires_auth(self):
        res = self.client.get("/api/customers/")
        self.assertEqual(res.status_code, 401)  # no token => 401

    def test_mecanico_can_list_but_cannot_create_customer(self):
        # listar (view_customer)
        res = self.client.get("/api/customers/", **jwt_headers("mecanico_test", "mecanico123"))
        self.assertEqual(res.status_code, 200)

        # crear (add_customer) debería ser 403 para Mecanico
        body = {"type": "PERSON", "name": "Cliente Mec", "is_active": True}
        res = self.client.post("/api/customers/", body, format="json",
                               **jwt_headers("mecanico_test", "mecanico123"))
        self.assertIn(res.status_code, (401, 403))
        self.assertEqual(res.status_code, 403)

    def test_asesor_can_create_customer(self):
        _id, _ = self._create_customer(name="Juan Perez")  # asserts dentro del helper

    # ----------------- Vehículos -----------------

    def test_asesor_can_create_vehicle(self):
        cust_id, _ = self._create_customer(name="Temp")
        _veh_id, _ = self._create_vehicle(owner_id=cust_id, plate="P123-456")

    def test_mecanico_cannot_delete_vehicle(self):
        # Prepara un vehículo propiedad de un customer
        cust_id, _ = self._create_customer(name="Temp2")
        veh_id, _ = self._create_vehicle(owner_id=cust_id, plate="P999-000", brand="Nissan", model="Sentra", year=2020, mileage_km=10000)

        # Intento de eliminar como Mecanico => 403
        res = self.client.delete(f"/api/vehicles/{veh_id}/",
                                 **jwt_headers("mecanico_test", "mecanico123"))
        self.assertEqual(res.status_code, 403)

    # ----------------- Catálogo (Service/Part) -----------------

    def test_asesor_can_create_service_and_part(self):
        s = {
            "code": "REV-GEN",
            "name": "Revision general",
            "description": "Chequeo basico",
            "labor_minutes": 60,
            "price": "25.00",
            "is_active": True,
        }
        sr = self.client.post("/api/services/", s, format="json",
                              **jwt_headers("asesor_test", "asesor123"))
        self.assertEqual(sr.status_code, 201, sr.content)

        p = {
            "sku": "FILT-ACEITE-001",
            "name": "Filtro de aceite",
            "unit": "UNI",
            "stock": "5.00",
            "cost": "3.00",
            "price": "6.50",
            "is_active": True,
        }
        pr = self.client.post("/api/parts/", p, format="json",
                              **jwt_headers("asesor_test", "asesor123"))
        self.assertEqual(pr.status_code, 201, pr.content)

    # ----------------- WorkOrders -----------------

    def test_asesor_can_create_workorder(self):
        cust_id, _ = self._create_customer(name="WO Temp")
        veh_id, _ = self._create_vehicle(owner_id=cust_id, plate="W123-456", brand="Honda", model="Civic", year=2017, mileage_km=70000)

        wo = {
            "number": "WO-0001",
            "status": "OPEN",
            "complaint": "Ruidos en suspension",
            "customer": cust_id,
            "vehicle": veh_id,
        }
        res = self.client.post("/api/workorders/", wo, format="json",
                               **jwt_headers("asesor_test", "asesor123"))
        self.assertEqual(res.status_code, 201, res.content)

    # ----------------- Auth básica -----------------

    def test_jwt_refresh_works(self):
        # Obtiene par tokens
        res = self.client.post("/api/auth/jwt/create/", {"username": "asesor_test", "password": "asesor123"}, format="json")
        self.assertEqual(res.status_code, 200, res.content)
        refresh = res.data["refresh"]

        # Refresca access
        rr = self.client.post("/api/auth/jwt/refresh/", {"refresh": refresh}, format="json")
        self.assertEqual(rr.status_code, 200, rr.content)
        self.assertIn("access", rr.data)