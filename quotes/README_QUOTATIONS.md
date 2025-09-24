
# App `quotes/` – Cotizaciones

## Instalación rápida
1. Copia la carpeta `quotes/` al directorio de apps de tu proyecto (junto a `customers/`, `vehicles/`, `catalog/`, `workorders/`).
2. Añade `"quotes"` a `INSTALLED_APPS` en `settings.py`.
3. Incluye sus rutas en `core/urls.py` o donde concentres routers:
   ```python
   from django.urls import path, include
   from quotes.urls import router as quotes_router

   urlpatterns = [
       # ...
       path("api/", include(quotes_router.urls)),
   ]
   ```
4. Crea migraciones y aplica:
   ```bash
   python manage.py makemigrations quotes
   python manage.py migrate
   ```
5. (Opcional) Admin: ingresa a `/admin` y prueba crear cotizaciones con ítems.

## Endpoints
- `GET/POST /api/quotations/`
- `GET/PUT/PATCH/DELETE /api/quotations/{id}/`
- `POST /api/quotations/{id}/approve/`
- `POST /api/quotations/{id}/to-workorder/`

## Notas
- Requiere apps `customers`, `vehicles`, `catalog`, `workorders` ya instaladas.
- Permisos: reutiliza `core.permissions.WriteRequiresAdminOrAsesor` si existe; si no, permite autenticados.
- Totales se recalculan al crear/actualizar cotización.
