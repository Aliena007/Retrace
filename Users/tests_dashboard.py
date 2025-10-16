from django.test import TestCase, Client
from django.contrib.auth.models import User


class DashboardViewTests(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpass'
        User.objects.create_user(self.username, 'test@example.com', self.password)

    def test_dashboard_requires_login_and_renders(self):
        c = Client()
        # unauthenticated should redirect
        resp = c.get('/users/dashboard/')
        self.assertIn(resp.status_code, (302, 301))

        # login and retry
        self.assertTrue(c.login(username=self.username, password=self.password))
        resp = c.get('/users/dashboard/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '<title>Dashboard - Retrace', status_code=200)
