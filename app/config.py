import os
from urllib.parse import urlparse
from peewee import MySQLDatabase
from app.db import database


def load_env(env_path: str = ".env") -> None:
    if not os.path.isfile(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception:
        pass


def env_db_uri() -> str:
    db_uri = os.getenv("DB_URI")
    if db_uri:
        return db_uri
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "3306")
    name = os.getenv("DB_NAME", "lms")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    return f"mysql://{user}:{password}@{host}:{port}/{name}"

def get_secret_key(default: str = "changeme") -> str:
    load_env()
    return os.getenv("SECRET_KEY", default)


def init_database_from_env() -> None:
    load_env()
    parsed = urlparse(env_db_uri())
    if parsed.scheme != "mysql":
        return
    name = (parsed.path or "/").lstrip("/") or None
    if not name:
        return
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 3306
    user = parsed.username or "root"
    password = parsed.password or ""
    database.initialize(MySQLDatabase(
        name,
        user=user,
        password=password,
        host=host,
        port=port,
        charset="utf8mb4",
    ))
