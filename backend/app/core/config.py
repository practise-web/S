from pydantic_settings import BaseSettings
import os


class KeycloakSettings(BaseSettings):
    KEYCLOAK_URL: str = os.environ.get("KEYCLOAK_URL")
    KEYCLOAK_REALM: str = os.environ.get("KEYCLOAK_REALM")
    KEYCLOAK_CLIENT_ID: str = os.environ.get("AUTH_CLIENT_ID")
    KEYCLOAK_CLIENT_SECRET: str = os.environ.get("AUTH_CLIENT_SECRET")
    KEYCLOAK_USERNAME: str = os.environ.get("KEYCLOAK_USERNAME")
    KEYCLOAK_PASSWORD: str = os.environ.get("KEYCLOAK_PASSWORD")

    @property
    def KEYCLOAK_TOKEN_URL(self):
        return f"{self.KEYCLOAK_URL}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/token"

    @property
    def KEYCLOAK_LOGOUT_URL(self):
        return f"{self.KEYCLOAK_URL}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/logout"

    @property
    def KEYCLOAK_JWK_URL(self):
        return f"{self.KEYCLOAK_URL}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/certs"

    def KEYCLOAK_EMAIL_ACTIONS_URL(self, user_id):
        return f"{self.KEYCLOAK_URL}/admin/realms/{self.KEYCLOAK_REALM}/users/{user_id}/execute-actions-email"

    def KEYCLOAK_RESET_PASSWORD_URL(self, user_id):
        return f"{self.KEYCLOAK_URL}/admin/realms/{self.KEYCLOAK_REALM}/users/{user_id}/reset-password"

    def KEYCLOAK_USERS_URL(self, user_id=None):
        if user_id:
            return f"{self.KEYCLOAK_URL}/admin/realms/{self.KEYCLOAK_REALM}/users/{user_id}"
        return f"{self.KEYCLOAK_URL}/admin/realms/{self.KEYCLOAK_REALM}/users"


kcsettings = KeycloakSettings()
