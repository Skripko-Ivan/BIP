import os


from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    KEYCLOAK_URL: str = "http://192.168.159.144:8090"
    REALM: str = "MyRealm"
    CLIENT_ID: str = "User"
    CLIENT_SECRET_KEY: str = "yJVr4CWGblznNF7nMWfsGk1swc8XIEEd"
    REDIRECT_URL: str = "http://192.168.159.144:8080/auth/callback"


settings = Settings()

