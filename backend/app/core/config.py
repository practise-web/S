from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import RedisDsn, Field


class KeycloakSettings(BaseSettings):
    KEYCLOAK_URL: str
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT_ID: str = Field(validation_alias="AUTH_CLIENT_ID")
    KEYCLOAK_CLIENT_SECRET: str = Field(validation_alias="AUTH_CLIENT_SECRET")
    KEYCLOAK_USERNAME: str
    KEYCLOAK_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Good practice: ignores extra env vars unrelated to this class
    )

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


class RedisSettings(BaseSettings):
    redis_url: RedisDsn = Field(alias="REDIS_URL")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


kcsettings = KeycloakSettings()  # type: ignore
redis_settings = RedisSettings()  # type: ignore
