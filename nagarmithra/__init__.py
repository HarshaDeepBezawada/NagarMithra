"""
NagarMitra Application Factory
================================
Creates and configures the Flask application instance.

Uses the Application Factory pattern so that multiple instances can be
created with different configurations (development, testing, production).
"""

import os
import logging
from flask import Flask, render_template
from config import config_map


def create_app(config_name: str | None = None) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        config_name: Configuration to use ('development', 'testing', 'production').
                     Defaults to the FLASK_CONFIG environment variable or 'development'.

    Returns:
        Configured Flask application instance.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')

    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'),
    )
    app.config.from_object(config_map.get(config_name, config_map['default']))

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ── Extensions ──────────────────────────────────────────────
    from nagarmithra.extensions import db, csrf
    db.init_app(app)
    csrf.init_app(app)

    # ── Blueprints ──────────────────────────────────────────────
    from nagarmithra.main.routes import main_bp
    from nagarmithra.complaints.routes import complaints_bp
    from nagarmithra.auth.routes import auth_bp
    from nagarmithra.admin.routes import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(complaints_bp, url_prefix='/complaints')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # ── CLI Commands ────────────────────────────────────────────
    register_cli_commands(app)

    # ── Error Handlers ──────────────────────────────────────────
    register_error_handlers(app)

    # ── Create Tables ───────────────────────────────────────────
    with app.app_context():
        from nagarmithra import models  # noqa: F401 — triggers model registration
        db.create_all()

    # ── Logging ─────────────────────────────────────────────────
    if not app.debug and not app.testing:
        logging.basicConfig(level=logging.INFO)
        app.logger.setLevel(logging.INFO)
        app.logger.info('NagarMitra application starting')

    return app


def register_cli_commands(app: Flask) -> None:
    """Register custom Flask CLI commands."""
    import click
    from werkzeug.security import generate_password_hash
    from nagarmithra.extensions import db
    from nagarmithra.models import Admin

    @app.cli.command('create-admin')
    @click.option('--username', prompt=True, help='Administrator username')
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True,
                  help='Administrator password')
    def create_admin(username: str, password: str):
        """Create a new administrator account."""
        existing = Admin.query.filter_by(username=username).first()
        if existing:
            click.echo(f'Error: Administrator "{username}" already exists.')
            return

        admin = Admin(
            username=username,
            password_hash=generate_password_hash(password),
        )
        db.session.add(admin)
        db.session.commit()
        click.echo(f'Administrator "{username}" created successfully.')

    @app.cli.command('init-db')
    def init_db():
        """Initialize the database (create all tables)."""
        db.create_all()
        click.echo('Database tables created.')


def register_error_handlers(app: Flask) -> None:
    """Register custom error pages."""

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(413)
    def file_too_large(e):
        return render_template('errors/413.html'), 413
