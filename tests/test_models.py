"""
NagarMitra Model Tests
=======================
Tests for database models, relationships, and data integrity.
"""

from nagarmithra.models import Complaint, StatusHistory, Admin, generate_reference
from werkzeug.security import generate_password_hash, check_password_hash


class TestGenerateReference:
    """Tests for the complaint reference number generator."""

    def test_format(self):
        """Reference should start with 'NM-' followed by 8 uppercase hex characters."""
        ref = generate_reference()
        assert ref.startswith('NM-')
        assert len(ref) == 11  # 'NM-' + 8 chars
        assert ref[3:].isalnum()

    def test_uniqueness(self):
        """Generated references should be unique (probabilistic test)."""
        refs = {generate_reference() for _ in range(100)}
        assert len(refs) == 100  # All 100 should be different


class TestComplaintModel:
    """Tests for the Complaint model."""

    def test_create_complaint(self, db):
        """A new complaint should be persisted with default values."""
        c = Complaint(
            citizen_name='John Doe',
            citizen_contact='john@example.com',
            title='Pothole on Main Street',
            description='Large pothole causing accidents. Very dangerous for bikes and cars.',
            category='roads',
            priority='high',
            location='100 Main Street',
        )
        db.session.add(c)
        db.session.commit()

        saved = Complaint.query.first()
        assert saved is not None
        assert saved.citizen_name == 'John Doe'
        assert saved.status == 'submitted'  # Default status
        assert saved.reference.startswith('NM-')
        assert saved.created_at is not None

    def test_unique_reference(self, db):
        """Two complaints should have different reference numbers."""
        c1 = Complaint(citizen_name='A', citizen_contact='a@a.com',
                       title='Issue one', description='Test description one details here.',
                       category='roads', location='Loc A')
        c2 = Complaint(citizen_name='B', citizen_contact='b@b.com',
                       title='Issue two', description='Test description two details here.',
                       category='water', location='Loc B')
        db.session.add_all([c1, c2])
        db.session.commit()

        assert c1.reference != c2.reference

    def test_status_history_relationship(self, db, sample_complaint):
        """A complaint should be linked to its status history entries."""
        history = StatusHistory(
            complaint_id=sample_complaint.id,
            old_status='submitted',
            new_status='in_progress',
            note='Being investigated',
        )
        db.session.add(history)
        db.session.commit()

        entries = sample_complaint.status_history.all()
        assert len(entries) == 1
        assert entries[0].new_status == 'in_progress'


class TestAdminModel:
    """Tests for the Admin model."""

    def test_create_admin(self, db):
        """An admin should be created with a hashed password."""
        pw_hash = generate_password_hash('secretpass')
        admin = Admin(username='admin1', password_hash=pw_hash)
        db.session.add(admin)
        db.session.commit()

        saved = Admin.query.first()
        assert saved.username == 'admin1'
        assert saved.is_active is True
        assert check_password_hash(saved.password_hash, 'secretpass')
        assert not check_password_hash(saved.password_hash, 'wrongpass')

    def test_unique_username(self, db):
        """Duplicate admin usernames should raise an error."""
        import sqlalchemy
        admin1 = Admin(username='unique', password_hash='hash1')
        admin2 = Admin(username='unique', password_hash='hash2')
        db.session.add(admin1)
        db.session.commit()
        db.session.add(admin2)
        try:
            db.session.commit()
            assert False, 'Should have raised IntegrityError'
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()


class TestStatusHistoryModel:
    """Tests for the StatusHistory model."""

    def test_create_history(self, db, sample_complaint, admin_user):
        """A status history entry should record the change details."""
        h = StatusHistory(
            complaint_id=sample_complaint.id,
            old_status='submitted',
            new_status='acknowledged',
            note='Received and noted',
            admin_id=admin_user.id,
        )
        db.session.add(h)
        db.session.commit()

        saved = StatusHistory.query.first()
        assert saved.old_status == 'submitted'
        assert saved.new_status == 'acknowledged'
        assert saved.admin.username == 'testadmin'
        assert saved.complaint.reference == sample_complaint.reference
