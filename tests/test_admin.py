"""
NagarMitra Admin Dashboard Tests
=================================
Tests for the admin dashboard, complaint management, and status updates.
"""

from nagarmithra.models import Complaint, StatusHistory


class TestDashboard:
    """Tests for the admin dashboard."""

    def test_dashboard_loads(self, logged_in_client, sample_complaint):
        """The dashboard should load with complaint data."""
        response = logged_in_client.get('/admin/dashboard')
        assert response.status_code == 200
        assert sample_complaint.reference.encode() in response.data

    def test_dashboard_stats(self, logged_in_client, sample_complaint):
        """Dashboard should show accurate statistics."""
        response = logged_in_client.get('/admin/dashboard')
        assert response.status_code == 200
        # Should show total count
        assert b'1' in response.data

    def test_dashboard_search(self, logged_in_client, sample_complaint):
        """Search should filter complaints by reference."""
        response = logged_in_client.get(
            f'/admin/dashboard?q={sample_complaint.reference}'
        )
        assert response.status_code == 200
        assert sample_complaint.reference.encode() in response.data

    def test_dashboard_filter_status(self, logged_in_client, sample_complaint):
        """Filtering by status should show matching complaints."""
        response = logged_in_client.get('/admin/dashboard?status=submitted')
        assert response.status_code == 200
        assert sample_complaint.reference.encode() in response.data

    def test_dashboard_filter_no_results(self, logged_in_client, sample_complaint):
        """Filtering by a non-matching status should show empty results."""
        response = logged_in_client.get('/admin/dashboard?status=resolved')
        assert response.status_code == 200
        assert b'No complaints found' in response.data


class TestComplaintDetail:
    """Tests for the admin complaint detail page."""

    def test_detail_page_loads(self, logged_in_client, sample_complaint):
        """The complaint detail page should load with all complaint data."""
        response = logged_in_client.get(f'/admin/complaint/{sample_complaint.id}')
        assert response.status_code == 200
        assert sample_complaint.title.encode() in response.data

    def test_detail_page_404(self, logged_in_client):
        """A non-existent complaint should return 404."""
        response = logged_in_client.get('/admin/complaint/9999')
        assert response.status_code == 404


class TestStatusUpdate:
    """Tests for updating complaint status."""

    def test_update_status(self, logged_in_client, sample_complaint, app):
        """Updating a complaint status should save the change and create history."""
        response = logged_in_client.post(
            f'/admin/complaint/{sample_complaint.id}',
            data={
                'status': 'in_progress',
                'priority': 'high',
                'admin_notes': 'Investigation started',
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

        # Verify the complaint was updated
        with app.app_context():
            complaint = Complaint.query.get(sample_complaint.id)
            assert complaint.status == 'in_progress'

            # Verify status history was created
            history = StatusHistory.query.filter_by(
                complaint_id=complaint.id
            ).first()
            assert history is not None
            assert history.old_status == 'submitted'
            assert history.new_status == 'in_progress'

    def test_resolve_complaint(self, logged_in_client, sample_complaint, app):
        """Resolving a complaint should set the resolved_at timestamp."""
        logged_in_client.post(
            f'/admin/complaint/{sample_complaint.id}',
            data={
                'status': 'resolved',
                'priority': 'high',
                'admin_notes': 'Streetlight has been repaired',
            },
            follow_redirects=True,
        )

        with app.app_context():
            complaint = Complaint.query.get(sample_complaint.id)
            assert complaint.status == 'resolved'
            assert complaint.resolved_at is not None


class TestCSVExport:
    """Tests for the CSV export feature."""

    def test_export_csv(self, logged_in_client, sample_complaint):
        """CSV export should return a downloadable file with complaint data."""
        response = logged_in_client.get('/admin/export/csv')
        assert response.status_code == 200
        assert response.content_type == 'text/csv; charset=utf-8'
        assert sample_complaint.reference.encode() in response.data


class TestEndToEndWorkflow:
    """End-to-end test of the complete complaint workflow."""

    def test_full_workflow(self, client, admin_user, app):
        """
        Complete workflow:
        1. Submit complaint → 2. Track it → 3. Admin updates status →
        4. Track again to see update
        """
        # Step 1: Submit a complaint
        response = client.post('/complaints/report', data={
            'citizen_name': 'Workflow Test User',
            'citizen_contact': 'workflow@test.com',
            'title': 'Water leakage on Oak Avenue',
            'description': 'Continuous water leakage from a broken pipe on Oak Avenue. '
                           'The road is getting flooded and damaging nearby property.',
            'category': 'water',
            'priority': 'critical',
            'location': 'Oak Avenue, Block C',
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'NM-' in response.data

        # Get the complaint reference
        with app.app_context():
            complaint = Complaint.query.filter_by(title='Water leakage on Oak Avenue').first()
            assert complaint is not None
            ref = complaint.reference
            complaint_id = complaint.id

        # Step 2: Track the complaint
        response = client.post('/complaints/track', data={
            'reference': ref,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert ref.encode() in response.data
        assert b'workflow@test.com' not in response.data  # Privacy check

        # Step 3: Admin logs in and updates status
        client.post('/auth/login', data={
            'username': 'testadmin',
            'password': 'testpassword123',
        })

        response = client.post(f'/admin/complaint/{complaint_id}', data={
            'status': 'in_progress',
            'priority': 'critical',
            'admin_notes': 'Plumber dispatched to location',
        }, follow_redirects=True)
        assert response.status_code == 200

        # Step 4: Mark as resolved
        response = client.post(f'/admin/complaint/{complaint_id}', data={
            'status': 'resolved',
            'priority': 'critical',
            'admin_notes': 'Pipe repaired, leak fixed',
        }, follow_redirects=True)
        assert response.status_code == 200

        # Step 5: Track again — should show resolved status
        client.get('/auth/logout')  # Logout first
        response = client.post('/complaints/track', data={
            'reference': ref,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Resolved' in response.data or b'resolved' in response.data

        # Step 6: Verify dashboard requires login
        response = client.get('/admin/dashboard')
        assert response.status_code == 302  # Should redirect to login
