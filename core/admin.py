# core/admin.py
from django.contrib import admin
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("name", "content_type", "codename")
    search_fields = ("name", "codename", "content_type__app_label", "content_type__model")
    list_filter = ("content_type__app_label",)

class GroupAdmin(DjangoGroupAdmin):
    # <- esto obliga el widget de dos listas (izq/der)
    filter_horizontal = ("permissions",)

    # y nos aseguramos de que se carguen TODOS los permisos y ordenados
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == "permissions":
            qs = Permission.objects.select_related("content_type").order_by(
                "content_type__app_label", "content_type__model", "codename"
            )
            kwargs["queryset"] = qs
        return super().formfield_for_manytomany(db_field, request, **kwargs)

# Reemplaza el admin de Group por el nuestro
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
