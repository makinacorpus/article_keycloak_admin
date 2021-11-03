import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class KeycloakUser(AbstractUser):
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    email = models.EmailField(unique=True)

    keycloak_uuid = models.UUIDField(
         editable=False, unique=True, default=uuid.uuid4
    )
