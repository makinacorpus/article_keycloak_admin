import uuid

from django.contrib import admin

# Register your models here.
from accounts.helpers import KeycloakHelper
from accounts.models import KeycloakUser


@admin.register(KeycloakUser)
class UserAdmin(admin.ModelAdmin):
    exclude = ["keycloak_uuid", "date_joined", "password"]
    keycloak_connection = KeycloakHelper()

    def save_model(self, request, obj, form, change):
        if not change:  # User account creation
            super().save_model(request, obj, form, change)

            keycloak_id = self.keycloak_connection.create_user(
                obj.email, obj.email
            )
            obj.keycloak_uuid = keycloak_id
        super().save_model(request, obj, form, change)
