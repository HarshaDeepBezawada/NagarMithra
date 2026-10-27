"""
NagarMitra Database Models
===========================
Defines the SQLAlchemy ORM models for the complaint management system.

Models:
    - Complaint: A civic issue reported by a citizen.
    - StatusHistory: An audit trail of every status change for a complaint.
    - Admin: An administrator who can manage complaints.
"""

import uuid
from datetime import datetime, timezone

from nagarmithra.extensions import db


# ── Constants ────────────────────────────────────────────────────────────────

CATEGORIES = [
    ('roads', 'Roads & Potholes'),
    ('garbage', 'Garbage & Sanitation'),
    ('water', 'Water Supply & Leakage'),
    ('streetlights', 'Streetlights & Public Infrastructure'),
    ('drainage', 'Drainage & Sewage'),
    ('other', 'Other'),
]

PRIORITIES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('critical', 'Critical'),
]

STATUSES = [
    ('submitted', 'Submitted'),
    ('acknowledged', 'Acknowledged'),
    ('in_progress', 'In Progress'),
    ('resolved', 'Resolved'),
    ('rejected', 'Rejected'),
]


def generate_reference() -> str:
    """
    Generate a unique, human-readable complaint reference number.
    Format: NM-XXXXXXXX (8 hex characters from a UUID4).
    """
    return 'NM-' + uuid.uuid4().hex[:8].upper()


class Complaint(db.Model):
    """
    Represents a civic complaint submitted by a citizen.

    Attributes:
        id: Internal auto-increment primary key.
        reference: Public-facing unique reference number (e.g., NM-A1B2C3D4).
        citizen_name: Name of the person reporting the issue.
        citizen_contact: Phone number or email of the reporter.
        title: Short summary of the issue.
        description: Detailed description of the problem.
        category: Type of civic issue (roads, garbage, water, etc.).
        priority: Severity level (low, medium, high, critical).
        location: Address or description of where the issue is located.
        image_filename: Optional uploaded photograph filename.
        status: Current complaint status.
        admin_notes: Notes added by the administrator.
        created_at: When the complaint was submitted.
        updated_at: When the complaint was last modified.
        resolved_at: When the complaint was marked as resolved.
    """
    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(20), unique=True, nullable=False, default=generate_reference, index=True)
    citizen_name = db.Column(db.String(100), nullable=False)
    citizen_contact = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), nullable=False, default='medium')
    location = db.Column(db.String(300), nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='submitted')
    admin_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    resolved_at = db.Column(db.DateTime, nullable=True)

    # Relationship: one complaint has many status history entries
    status_history = db.relationship('StatusHistory', backref='complaint',
                                     lazy='dynamic', order_by='StatusHistory.created_at.desc()')

    def __repr__(self) -> str:
        return f'<Complaint {self.reference}: {self.title[:30]}>'


class StatusHistory(db.Model):
    """
    Audit trail entry for a complaint status change.

    Every time an administrator changes a complaint's status, a new
    StatusHistory record is created to maintain a complete audit trail.
    """
    __tablename__ = 'status_history'

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False, index=True)
    old_status = db.Column(db.String(20), nullable=False)
    new_status = db.Column(db.String(20), nullable=False)
    note = db.Column(db.Text, nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationship to Admin
    admin = db.relationship('Admin', backref='status_changes')

    def __repr__(self) -> str:
        return f'<StatusHistory {self.old_status} → {self.new_status}>'


class Admin(db.Model):
    """
    Administrator account for the complaint management dashboard.

    Passwords are stored as hashes using Werkzeug's security utilities.
    Plaintext passwords are NEVER stored.
    """
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f'<Admin {self.username}>'
