"""
Admin Blueprint
================
Protected routes for the administrator dashboard, complaint management,
status updates, and data export.
"""

from datetime import datetime, timezone
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, session,
    Response,
)

from nagarmithra.extensions import db
from nagarmithra.models import Complaint, StatusHistory, Admin, CATEGORIES, STATUSES, PRIORITIES
from nagarmithra.forms import StatusUpdateForm
from nagarmithra.auth import login_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Administrator dashboard with complaint metrics, search, filter, and pagination.

    Supports query parameters:
        - q: search by reference or title
        - status: filter by complaint status
        - category: filter by category
        - priority: filter by priority
        - page: pagination page number
    """
    page = request.args.get('page', 1, type=int)
    per_page = 15

    # Build query with optional filters
    query = Complaint.query

    search_q = request.args.get('q', '', type=str).strip()
    if search_q:
        query = query.filter(
            db.or_(
                Complaint.reference.ilike(f'%{search_q}%'),
                Complaint.title.ilike(f'%{search_q}%'),
            )
        )

    status_filter = request.args.get('status', '', type=str)
    if status_filter:
        query = query.filter_by(status=status_filter)

    category_filter = request.args.get('category', '', type=str)
    if category_filter:
        query = query.filter_by(category=category_filter)

    priority_filter = request.args.get('priority', '', type=str)
    if priority_filter:
        query = query.filter_by(priority=priority_filter)

    # Order by most recent first, then paginate
    pagination = query.order_by(Complaint.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Dashboard statistics (always from full database, not filtered)
    stats = {
        'total': Complaint.query.count(),
        'submitted': Complaint.query.filter_by(status='submitted').count(),
        'acknowledged': Complaint.query.filter_by(status='acknowledged').count(),
        'in_progress': Complaint.query.filter_by(status='in_progress').count(),
        'resolved': Complaint.query.filter_by(status='resolved').count(),
        'rejected': Complaint.query.filter_by(status='rejected').count(),
        'high_priority': Complaint.query.filter(
            Complaint.priority.in_(['high', 'critical'])
        ).count(),
    }

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        complaints=pagination.items,
        pagination=pagination,
        search_q=search_q,
        status_filter=status_filter,
        category_filter=category_filter,
        priority_filter=priority_filter,
        categories=CATEGORIES,
        statuses=STATUSES,
        priorities=PRIORITIES,
    )


@admin_bp.route('/complaint/<int:complaint_id>', methods=['GET', 'POST'])
@login_required
def complaint_detail(complaint_id: int):
    """
    View and update a specific complaint.

    GET: Display complaint details with status history.
    POST: Update status, priority, and/or admin notes.
          Records all changes in the status history audit trail.
    """
    complaint = Complaint.query.get_or_404(complaint_id)
    form = StatusUpdateForm(obj=complaint)

    if form.validate_on_submit():
        old_status = complaint.status
        new_status = form.status.data
        old_priority = complaint.priority
        new_priority = form.priority.data
        notes = form.admin_notes.data.strip() if form.admin_notes.data else ''

        # Track what changed for the status history note
        changes = []

        if old_status != new_status:
            complaint.status = new_status
            changes.append(f'Status: {old_status} → {new_status}')

            # Record resolved timestamp
            if new_status == 'resolved':
                complaint.resolved_at = datetime.now(timezone.utc)
            elif old_status == 'resolved':
                complaint.resolved_at = None  # Reopened

        if old_priority != new_priority:
            complaint.priority = new_priority
            changes.append(f'Priority: {old_priority} → {new_priority}')

        if notes:
            complaint.admin_notes = notes

        # Create status history entry if anything changed
        if changes or notes:
            history_note = '; '.join(changes)
            if notes:
                history_note += f' | Note: {notes}' if history_note else f'Note: {notes}'

            history = StatusHistory(
                complaint_id=complaint.id,
                old_status=old_status,
                new_status=new_status if old_status != new_status else old_status,
                note=history_note,
                admin_id=session.get('admin_id'),
            )
            db.session.add(history)

        try:
            db.session.commit()
            flash('Complaint updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Failed to update complaint. Please try again.', 'danger')

        return redirect(url_for('admin.complaint_detail', complaint_id=complaint.id))

    # Pre-fill form with current values
    form.status.data = complaint.status
    form.priority.data = complaint.priority
    form.admin_notes.data = complaint.admin_notes or ''

    history = complaint.status_history.all()

    return render_template(
        'admin/complaint_detail.html',
        complaint=complaint,
        form=form,
        history=history,
        categories=dict(CATEGORIES),
        statuses=dict(STATUSES),
        priorities=dict(PRIORITIES),
    )


@admin_bp.route('/export/csv')
@login_required
def export_csv():
    """Export all complaints as a CSV file for offline analysis."""
    complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()

    def generate():
        yield 'Reference,Title,Category,Priority,Status,Location,Citizen Name,Created,Updated,Resolved\n'
        for c in complaints:
            resolved = c.resolved_at.strftime('%Y-%m-%d %H:%M') if c.resolved_at else ''
            # Escape double quotes in CSV fields
            title = c.title.replace('"', '""')
            location = c.location.replace('"', '""')
            name = c.citizen_name.replace('"', '""')
            yield (
                f'{c.reference},"{title}",{c.category},{c.priority},{c.status},'
                f'"{location}","{name}",'
                f'{c.created_at.strftime("%Y-%m-%d %H:%M")},'
                f'{c.updated_at.strftime("%Y-%m-%d %H:%M")},{resolved}\n'
            )

    return Response(
        generate(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=nagarmitra_complaints.csv'},
    )
