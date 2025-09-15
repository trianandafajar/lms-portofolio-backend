from peewee import (
    Model,
    AutoField,
    CharField,
    BooleanField,
    DateTimeField,
)
from app.db import database

class BaseModel(Model):
    class Meta:
        database = database

class User(BaseModel):
    id = AutoField()
    email = CharField(max_length=255, unique=True, index=True)
    password_hash = CharField(max_length=255)
    is_active = BooleanField(default=True)
    created_at = DateTimeField()
    updated_at = DateTimeField()

    class Meta:
        table_name = "users"
