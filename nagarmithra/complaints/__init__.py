"""
Complaints Blueprint
=====================
Handles complaint submission, tracking, and uploaded image serving.
"""

import os
import uuid
from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    current_app, send_from_directory,
)
from werkzeug.utils import secure_filename

from nagarmithra.extensions import db
from nagarmithra.models import Complaint
from nagarmithra.forms import ComplaintForm, TrackingForm

complaints_bp = Blueprint('complaints', __name__)


def _allowed_file(filename: str) -> bool:
    """Check if an uploaded file has an allowed image extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def _save_image(file) -> str | None:
    """
    Save an uploaded image with a safe, unique filename.

    Returns the generated filename or None if no file was provided.
    Prevents path traversal by generating a UUID-based filename.
    """
    if file and file.filename:
        original = secure_filename(file.filename)
        if not original:
            return None
        ext = original.rsplit('.', 1)[1].lower() if '.' in original else 'jpg'
        safe_name = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], safe_name)
        file.save(filepath)
        return safe_name
    return None


@complaints_bp.route('/report', methods=['GET', 'POST'])
def report():
    """
    Complaint submission page.

    GET: Display the complaint form.
    POST: Validate inputs, save the complaint to the database,
          and display the generated reference number.
    """
    form = ComplaintForm()

    if form.validate_on_submit():
        try:
            # Handle optional image upload
            image_filename = None
            if form.image.data:
                image_filename = _save_image(form.image.data)

            complaint = Complaint(
                citizen_name=form.citizen_name.data.strip(),
                citizen_contact=form.citizen_contact.data.strip(),
                title=form.title.data.strip(),
                description=form.description.data.strip(),
                category=form.category.data,
                priority=form.priority.data,
                location=form.location.data.strip(),
                image_filename=image_filename,
            )
            db.session.add(complaint)
            db.session.commit()

            flash(f'Complaint submitted successfully! Your reference number is: {complaint.reference}',
                  'success')
            return redirect(url_for('complaints.success', reference=complaint.reference))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Complaint submission failed: {e}')
            flash('An error occurred while submitting your complaint. Please try again.', 'danger')

    return render_template('report.html', form=form)


@complaints_bp.route('/success/<reference>')
def success(reference: str):
    """Display the success page with the complaint reference number."""
    complaint = Complaint.query.filter_by(reference=reference).first_or_404()
    return render_template('success.html', complaint=complaint)


@complaints_bp.route('/track', methods=['GET', 'POST'])
def track():
    """
    Complaint tracking page.

    Citizens enter their reference number and see the current status
    of their complaint. Private contact information is NOT displayed.
    """
    form = TrackingForm()
    complaint = None

    if form.validate_on_submit():
        ref = form.reference.data.strip().upper()
        complaint = Complaint.query.filter_by(reference=ref).first()
        if not complaint:
            flash('No complaint found with that reference number. '
                  'Please check and try again.', 'warning')

    return render_template('track.html', form=form, complaint=complaint)


@complaints_bp.route('/uploads/<filename>')
def uploaded_file(filename: str):
    """Serve an uploaded complaint image securely."""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
