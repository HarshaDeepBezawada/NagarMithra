"""
Flask Extensions
=================
Extension instances are created here and initialized in the application
factory (create_app). This avoids circular import problems.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

# Database ORM
db = SQLAlchemy()

# CSRF protection for forms
csrf = CSRFProtect()
