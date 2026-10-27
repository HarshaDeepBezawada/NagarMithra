"""
Main Blueprint — Public-Facing Pages
======================================
Handles the landing page and general public routes.
"""

from flask import Blueprint, render_template
from nagarmithra.extensions import db
from nagarmithra.models import Complaint

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    Landing page with live database-backed statistics.

    Displays the total number of complaints broken down by status,
    queried directly from the database so numbers are always accurate.
    """
    stats = {
        'total': db.session.query(Complaint).count(),
        'submitted': db.session.query(Complaint).filter_by(status='submitted').count(),
        'in_progress': db.session.query(Complaint).filter_by(status='in_progress').count(),
        'resolved': db.session.query(Complaint).filter_by(status='resolved').count(),
    }
    return render_template('index.html', stats=stats)
