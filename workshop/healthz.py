from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db import connections

@require_GET
def healthz(request):
    db_ok = True
    try:
        with connections['default'].cursor() as cursor:
            cursor.execute('SELECT 1')
    except Exception:
        db_ok = False
    return JsonResponse({'status': 'ok' if db_ok else 'degraded', 'db': db_ok})