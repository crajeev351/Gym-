import os
import click
from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from config import Config
from app.models import db, User, SiteSetting
from app.seed import seed_default_data

migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    login_manager.login_message = 'Please log in to access the admin portal.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register Blueprints
    from app.routes.public import public_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    # Global template context processor
    @app.context_processor
    def inject_global_settings():
        try:
            settings = SiteSetting.query.first()
            return {'site_settings': settings}
        except Exception:
            return {'site_settings': None}

    # Register custom CLI commands
    register_cli_commands(app)

    # Auto-create tables and seed default data if not present
    with app.app_context():
        try:
            db.create_all()
            seed_default_data()
        except Exception as e:
            app.logger.warning(f"Database initialization notice: {e}")

    return app


def register_cli_commands(app):
    @app.cli.command("create-admin")
    @click.option("--username", prompt=True, default="admin", help="Admin username")
    @click.option("--email", prompt=True, default="admin@fitnessjourney.com", help="Admin email address")
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Admin password")
    def create_admin(username, email, password):
        """CLI command to create or update the primary administrator account."""
        username = username.strip()
        email = email.strip().lower()

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            click.echo(f"Updating password for existing administrator: {existing_user.username}")
            existing_user.set_password(password)
            db.session.commit()
            click.secho(f"[OK] Administrator '{existing_user.username}' password updated successfully!", fg="green")
        else:
            click.echo(f"Creating new administrator: {username}")
            admin = User(username=username, email=email)
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            click.secho(f"[OK] Administrator '{username}' created successfully!", fg="green")
            click.secho(f"You can now log in at: /admin/login", fg="cyan")

    @app.cli.command("seed-db")
    def seed_db_command():
        """Force populate database with default Hero, Programs, Training Types, and Settings."""
        db.create_all()
        seed_default_data()
        click.secho("[OK] Database seeded with default fitness programs, training types, and settings!", fg="green")
