"""
NagarMitra Authentication Tests
================================
Tests for login, logout, and route protection.
"""


class TestLogin:
    """Tests for the admin login flow."""

    def test_login_page_loads(self, client):
        """The login page should return 200 and contain the form."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Administrator Login' in response.data or b'Sign In' in response.data

    def test_login_success(self, client, admin_user):
        """Valid credentials should redirect to the dashboard."""
        response = client.post('/auth/login', data={
            'username': 'testadmin',
            'password': 'testpassword123',
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'dashboard' in response.data

    def test_login_wrong_password(self, client, admin_user):
        """Invalid password should show an error message."""
        response = client.post('/auth/login', data={
            'username': 'testadmin',
            'password': 'wrongpassword',
        }, follow_redirects=True)
        assert b'Invalid username or password' in response.data

    def test_login_nonexistent_user(self, client, admin_user):
        """A non-existent username should show an error message."""
        response = client.post('/auth/login', data={
            'username': 'nobody',
            'password': 'testpassword123',
        }, follow_redirects=True)
        assert b'Invalid username or password' in response.data

    def test_logout(self, logged_in_client):
        """Logout should clear the session and redirect."""
        response = logged_in_client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'logged out' in response.data.lower()


class TestProtectedRoutes:
    """Tests that admin routes require authentication."""

    def test_dashboard_requires_login(self, client):
        """Accessing the dashboard without login should redirect to login."""
        response = client.get('/admin/dashboard')
        assert response.status_code == 302  # Redirect to login

    def test_complaint_detail_requires_login(self, client, sample_complaint):
        """Accessing complaint detail without login should redirect."""
        response = client.get(f'/admin/complaint/{sample_complaint.id}')
        assert response.status_code == 302

    def test_export_requires_login(self, client):
        """CSV export should require login."""
        response = client.get('/admin/export/csv')
        assert response.status_code == 302
