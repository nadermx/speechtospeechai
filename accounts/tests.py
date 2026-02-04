"""
Account and API tests for Speech to Speech AI

Run with: pytest accounts/tests.py -v
"""
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTests(TestCase):
    """Test CustomUser model"""

    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_confirm)

    def test_create_superuser(self):
        """Test creating a superuser"""
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_active)

    def test_user_has_api_token(self):
        """Test that new users get an API token"""
        user = User.objects.create_user(
            email='apiuser@example.com',
            password='testpass123'
        )
        self.assertIsNotNone(user.api_token)
        self.assertTrue(len(user.api_token) > 20)

    def test_user_uuid_is_generated(self):
        """Test that users get a UUID"""
        user = User.objects.create_user(
            email='uuiduser@example.com',
            password='testpass123'
        )
        self.assertIsNotNone(user.uuid)

    def test_default_credits(self):
        """Test that new users start with 0 credits"""
        user = User.objects.create_user(
            email='credits@example.com',
            password='testpass123'
        )
        self.assertEqual(user.credits, 0)


class AuthenticationTests(TestCase):
    """Test authentication flows"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='auth@example.com',
            password='authpass123'
        )

    def test_login_page_loads(self):
        """Test login page loads"""
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_signup_page_loads(self):
        """Test signup page loads"""
        response = self.client.get('/signup/')
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        """Test successful login"""
        response = self.client.post('/login/', {
            'email': 'auth@example.com',
            'password': 'authpass123'
        })
        # Should redirect to account or next page
        self.assertIn(response.status_code, [200, 302])

    def test_login_failure(self):
        """Test failed login with wrong password"""
        response = self.client.post('/login/', {
            'email': 'auth@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        # Should stay on login page with error

    def test_logout(self):
        """Test logout"""
        self.client.login(username='auth@example.com', password='authpass123')
        response = self.client.get('/logout/')
        self.assertIn(response.status_code, [200, 302])


class PageAccessTests(TestCase):
    """Test page access controls"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='access@example.com',
            password='accesspass123',
            is_confirm=True
        )

    def test_public_pages_accessible(self):
        """Test public pages are accessible without login"""
        public_urls = [
            '/',
            '/pricing/',
            '/api-docs/',
            '/models/',
            '/about/',
            '/contact/',
            '/privacy/',
            '/terms/',
            '/voice-cloning/',
            '/text-to-speech/',
            '/speech-to-text/',
            '/voice-conversion/',
            '/audio-enhancement/',
            '/speech-translation/',
            '/real-time-chat/',
            '/custom-training/',
        ]
        for url in public_urls:
            response = self.client.get(url)
            self.assertEqual(
                response.status_code, 200,
                f"Page {url} returned {response.status_code}"
            )

    def test_account_requires_login(self):
        """Test account page requires login"""
        response = self.client.get('/account/')
        self.assertIn(response.status_code, [302, 403])

    def test_account_accessible_when_logged_in(self):
        """Test account page accessible when logged in"""
        self.client.login(username='access@example.com', password='accesspass123')
        response = self.client.get('/account/')
        self.assertIn(response.status_code, [200, 302])


class RateLimitAPITests(TestCase):
    """Test rate limit API endpoint"""

    def setUp(self):
        self.client = Client()

    def test_rate_limit_endpoint_exists(self):
        """Test rate limit endpoint responds"""
        response = self.client.post(
            '/api/accounts/rate_limit/',
            content_type='application/json',
            data='{}'
        )
        # Should return 200 or 400, not 404/500
        self.assertIn(response.status_code, [200, 400, 403])


class ErrorLoggingTests(TestCase):
    """Test frontend error logging endpoint"""

    def setUp(self):
        self.client = Client()

    def test_log_error_endpoint(self):
        """Test error logging endpoint accepts POST"""
        response = self.client.post(
            '/api/log-error/',
            content_type='application/json',
            data='{"message": "Test error", "url": "https://example.com"}'
        )
        self.assertIn(response.status_code, [200, 201, 204])


class ContactFormTests(TestCase):
    """Test contact form functionality"""

    def setUp(self):
        self.client = Client()

    def test_contact_page_loads(self):
        """Test contact page loads"""
        response = self.client.get('/contact/')
        self.assertEqual(response.status_code, 200)

    def test_contact_form_has_csrf(self):
        """Test contact form has CSRF token"""
        response = self.client.get('/contact/')
        self.assertContains(response, 'csrfmiddlewaretoken')


class ToolPageTests(TestCase):
    """Test tool page content"""

    def setUp(self):
        self.client = Client()

    def test_text_to_speech_has_elements(self):
        """Test text-to-speech page has required elements"""
        response = self.client.get('/text-to-speech/')
        content = response.content.decode()

        # Check for key elements
        self.assertIn('textInput', content)
        self.assertIn('voiceSelect', content)
        self.assertIn('generateBtn', content)

    def test_voice_cloning_has_elements(self):
        """Test voice-cloning page has required elements"""
        response = self.client.get('/voice-cloning/')
        content = response.content.decode()

        self.assertIn('dropzone', content)
        self.assertIn('cloneBtn', content)

    def test_real_time_chat_has_elements(self):
        """Test real-time-chat page has required elements"""
        response = self.client.get('/real-time-chat/')
        content = response.content.decode()

        self.assertIn('callBtn', content)
        self.assertIn('chatMessages', content)
        self.assertIn('muteBtn', content)


class APIConfigurationTests(TestCase):
    """Test API configuration in templates"""

    def setUp(self):
        self.client = Client()

    def test_api_server_configured(self):
        """Test API_SERVER is set in page"""
        response = self.client.get('/voice-cloning/')
        content = response.content.decode()
        self.assertIn('API_SERVER', content)
        self.assertIn('api.', content)

    def test_speech_api_js_loaded(self):
        """Test speech-api.js is loaded"""
        response = self.client.get('/voice-cloning/')
        content = response.content.decode()
        self.assertIn('speech-api.js', content)


class UserAPITokenTests(TestCase):
    """Test API token functionality"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='token@example.com',
            password='tokenpass123',
            is_confirm=True
        )

    def test_api_key_in_page_when_logged_in(self):
        """Test API_KEY is injected when logged in"""
        self.client.login(username='token@example.com', password='tokenpass123')
        response = self.client.get('/voice-cloning/')
        content = response.content.decode()

        # Should have API_KEY set
        self.assertIn('API_KEY', content)
        self.assertIn(self.user.api_token, content)

    def test_no_api_key_when_logged_out(self):
        """Test API_KEY is not set when logged out"""
        response = self.client.get('/voice-cloning/')
        content = response.content.decode()

        # Should NOT have API_KEY variable with a value
        # But may have the JS that checks for it
        self.assertNotIn(self.user.api_token, content)
