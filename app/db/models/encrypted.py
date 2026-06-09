from cryptography.fernet import Fernet
from sqlalchemy import event

from app.settings import settings

fernet = Fernet(bytes(settings.fernet_key, encoding="utf-8"))


class EncryptedCredentialsMixin:
    @classmethod
    def encrypt_value(cls, value: str) -> str:
        return str(fernet.encrypt(bytes(value, encoding="utf-8")), encoding="utf-8")

    @classmethod
    def decrypt_value(cls, value: str) -> str:
        return str(fernet.decrypt(value), encoding="utf-8")

    @classmethod
    def register_encrypted_fields(cls, *fields: str) -> None:
        @event.listens_for(cls, "before_insert")
        @event.listens_for(cls, "before_update")
        def encrypt_before_persist(mapper, connection, target):
            for field in fields:
                setattr(target, field, cls.encrypt_value(getattr(target, field)))

        @event.listens_for(cls, "load")
        def decrypt_on_load(target, context):
            for field in fields:
                setattr(target, field, cls.decrypt_value(getattr(target, field)))
