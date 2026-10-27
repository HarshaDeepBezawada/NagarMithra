"""
NagarMitra Configuration Module
================================
Defines application configuration classes for different environments.
Secrets are loaded from environment variables for security.
"""

import os
from dotenv import load_dotenv

# Load .env file if it exists (development convenience)
load_dotenv()


class Config:
    """Base configuration shared across all environments."""

    # Secret key for session signing and CSRF protection.
    # MUST be set via environment variable in production.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File upload settings
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max upload size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class DevelopmentConfig(Config):
    """Development configuration — debug mode enabled, local SQLite database."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nagarmitra.db')
    )


class TestingConfig(Config):
    """Testing configuration — separate in-memory database, CSRF disabled for test client."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # Disable CSRF for automated testing
    SERVER_NAME = 'localhost'


class ProductionConfig(Config):
    """
    Production configuration — debug disabled, stricter security.
    In a real deployment, SECRET_KEY and DATABASE_URL MUST be set via environment variables.
    """
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nagarmitra.db')
    )
    SESSION_COOKIE_SECURE = True  # Requires HTTPS


# Map of configuration names to classes for easy selection
config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
