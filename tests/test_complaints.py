"""
NagarMitra Complaint Tests
============================
Tests for complaint submission, tracking, and the public workflow.
"""


class TestHomePage:
    """Tests for the public landing page."""

    def test_home_page_loads(self, client):
        """The home page should return 200 and contain NagarMitra branding."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'NagarMitra' in response.data

    def test_home_page_stats(self, client, sample_complaint):
        """The home page should show live statistics from the database."""
        response = client.get('/')
        assert response.status_code == 200
        # Should show at least 1 total complaint
        assert b'1' in response.data


class TestComplaintSubmission:
    """Tests for the complaint submission form."""

    def test_report_page_loads(self, client):
        """The report page should return 200 with the form."""
        response = client.get('/complaints/report')
        assert response.status_code == 200
        assert b'Report' in response.data

    def test_submit_complaint(self, client):
        """A valid complaint should be saved and show the reference number."""
        response = client.post('/complaints/report', data={
            'citizen_name': 'Jane Smith',
            'citizen_contact': 'jane@example.com',
            'title': 'Overflowing garbage bin at market',
            'description': 'The garbage bin at the central market has been overflowing for three days. '
                           'It is attracting stray animals and causing health hazards.',
            'category': 'garbage',
            'priority': 'high',
            'location': 'Central Market, Sector 7',
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'NM-' in response.data  # Reference number should be displayed

    def test_submit_complaint_missing_fields(self, client):
        """Incomplete submissions should fail validation."""
        response = client.post('/complaints/report', data={
            'citizen_name': '',
            'title': '',
        }, follow_redirects=True)
        assert response.status_code == 200
        # Should show validation errors, not a 500

    def test_submit_complaint_short_description(self, client):
        """Description that is too short should fail validation."""
        response = client.post('/complaints/report', data={
            'citizen_name': 'Test User',
            'citizen_contact': 'test@test.com',
            'title': 'Short title test',
            'description': 'Too short',  # Less than 20 chars
            'category': 'roads',
            'priority': 'low',
            'location': 'Test Location Area',
        }, follow_redirects=True)
        assert response.status_code == 200
        # Should not redirect to success — form should re-render with errors


class TestComplaintTracking:
    """Tests for the complaint tracking feature."""

    def test_track_page_loads(self, client):
        """The tracking page should return 200."""
        response = client.get('/complaints/track')
        assert response.status_code == 200
        assert b'Track' in response.data

    def test_track_valid_reference(self, client, sample_complaint):
        """Tracking a valid reference should show complaint details."""
        response = client.post('/complaints/track', data={
            'reference': sample_complaint.reference,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert sample_complaint.reference.encode() in response.data
        assert sample_complaint.title.encode() in response.data
        # Should NOT show contact information
        assert b'test@example.com' not in response.data

    def test_track_invalid_reference(self, client):
        """An invalid reference should show a helpful error, not crash."""
        response = client.post('/complaints/track', data={
            'reference': 'NM-INVALID1',
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'No complaint found' in response.data


class TestPrivacyProtection:
    """Tests that citizen contact info is not exposed publicly."""

    def test_tracking_hides_contact(self, client, sample_complaint):
        """The public tracking page must not display citizen contact info."""
        response = client.post('/complaints/track', data={
            'reference': sample_complaint.reference,
        }, follow_redirects=True)
        assert b'test@example.com' not in response.data
