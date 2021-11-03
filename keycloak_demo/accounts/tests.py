from unittest import mock
from unittest.mock import patch
from uuid import uuid4

from django.test import TestCase

# Create your tests here.
from django.contrib.admin import AdminSite
from django.urls import reverse

from accounts.admin import UserAdmin
from accounts.models import KeycloakUser


def get_admin_create_view_url(cls) -> str:
    """
    Given an object, returns the admin create view url for this object
    """
    return reverse("admin:{}_{}_add".format(cls._meta.app_label, cls.__name__.lower()))


class KeycloakTestCase(TestCase):
    def setUp(self):
        self.patcher = patch(
            "accounts.helpers.KeycloakAdmin.__init__", autospec=True, return_value=None
        )
        self.mock_keycloak_admin = self.patcher.start()  # Activation du patch nécessaire pour le rendre effectif
        self.addCleanup(self.patcher.stop)  # Désactivation du patch après le test


class AdminTestKeycloakInteraction(KeycloakTestCase):
    """
    Tests that admin endpoints correctly calls keycloak's one
    """

    def setUp(self):
        super().setUp()  # Bien penser à appeler le setUp() de la classe parente

        self.site = AdminSite()
        _ = UserAdmin(admin_site=self.site, model=KeycloakUser)
        self.admin_user = KeycloakUser.objects.create(is_superuser=True, is_staff=True, username="admin",
                                                      email="admin@example.com", keycloak_uuid=uuid4())

    @mock.patch("accounts.helpers.KeycloakAdmin.create_user", return_value=None)
    def test_user_create(
        self,
        mocked_create_user,
    ):
        uuid = uuid4()
        mocked_create_user.return_value = uuid

        payload = {
            "email": "test_user@example.com",
            "username": "username000",
        }
        self.client.force_login(self.admin_user)
        response = self.client.post(
            get_admin_create_view_url(KeycloakUser), data=payload, follow=True
        )
        self.assertEqual(response.status_code, 200)

        keycloak_payload = {
            "email": payload["email"],
            "username": payload["email"],  # USERNAME_FIELD = "email"
            "enabled": str(True),
        }
        mocked_create_user.assert_called_once_with(keycloak_payload)

        saved_user = KeycloakUser.objects.get(email=payload["email"])
        self.assertEqual(saved_user.keycloak_uuid, uuid)
        self.assertEqual(saved_user.email, payload["email"])


