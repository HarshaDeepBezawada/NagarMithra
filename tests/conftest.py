"""
NagarMitra Test Configuration
==============================
Shared pytest fixtures for all test modules.
"""

import pytest
from werkzeug.security import generate_password_hash

from nagarmithra import create_app
from nagarmithra.extensions import db as _db
from nagarmithra.models import Admin, Complaint


@pytest.fixture(scope='session')
def app():
    """Create a Flask application configured for testing."""
    app = create_app('testing')
    return app


@pytest.fixture(scope='function')
def db(app):
    """
    Create fresh database tables for each test function.
    Tables are dropped after each test to ensure isolation.
    """
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app, db):
    """Provide a Flask test client with a clean database."""
    return app.test_client()


@pytest.fixture
def admin_user(db):
    """Create a test administrator account and return it."""
    admin = Admin(
        username='testadmin',
        password_hash=generate_password_hash('testpassword123'),
        is_active=True,
    )
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture
def logged_in_client(client, admin_user):
    """Provide a test client with an authenticated admin session."""
    with client.session_transaction() as sess:
        sess['admin_id'] = admin_user.id
        sess['admin_username'] = admin_user.username
    return client


@pytest.fixture
def sample_complaint(db):
    """Create and return a sample complaint for testing."""
    complaint = Complaint(
        citizen_name='Test Citizen',
        citizen_contact='test@example.com',
        title='Broken streetlight near park',
        description='The streetlight near Central Park entrance has been broken for a week. '
                    'It is very dark and unsafe at night.',
        category='streetlights',
        priority='high',
        location='Central Park Entrance, Main Street',
    )
    db.session.add(complaint)
    db.session.commit()
    return complaint
