# Makes app a package
import click
from flask import Flask
from app.config import init_database_from_env
from app.seeds.seed_roles_permissions import seed_roles_permissions
from app.seeds.user_seeder import seed_users


def create_app():
    init_database_from_env()
    app = Flask(__name__)

    # CLI command untuk seed roles
    @app.cli.command("seed-roles")
    def seed_roles():
        """Seed default roles and permissions."""
        from app.db import database
        if database.is_closed():
            database.connect()
        seed_roles_permissions()
        if not database.is_closed():
            database.close()
        click.echo("✅ Roles & permissions seeded.")

    # CLI command untuk seed users
    @app.cli.command("seed-users")
    def seed_users_cmd():
        """Seed default users (admin, teacher, student)."""
        from app.db import database
        if database.is_closed():
            database.connect()
        seed_users()
        if not database.is_closed():
            database.close()
        click.echo("✅ Users seeded (admin, teacher, student).")

    return app
