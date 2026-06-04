from cryptography.fernet import Fernet

from app.settings import settings

fernet = Fernet(bytes(settings.fernet_key, encoding="utf-8"))


class EncryptedCredentialsMixin:
    @classmethod
    def encrypt_value(cls, value: str) -> str:
        return str(fernet.encrypt(bytes(value, encoding="utf-8")), encoding="utf-8")

    @classmethod
    def decrypt_value(cls, value: str) -> str:
        return str(fernet.decrypt(value), encoding="utf-8")
