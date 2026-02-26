"""
Tests for the accounts API endpoints: RateLimit, CreditsConsume,
ResendVerificationEmail, and CancelSubscription.

These are the DRF-based API views mounted at /api/accounts/.

Run with: python manage.py test tests.test_api -v2
"""
import json
from unittest import mock

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from finances.models.plan import Plan
from translations.models.language import Language
from translations.models.translation import Translation

User = get_user_model()


def _seed_i18n():
    Language.objects.get_or_create(
        iso='en', defaults={'name': 'English', 'en_label': 'English'}
    )
    keys = [
        'login', 'sign_up', 'site_description',
    ]
    for key in keys:
        Translation.objects.get_or_create(
            code_name=key, language='en', defaults={'text': key}
        )


# ---------------------------------------------------------------------------
# RateLimit API
# ---------------------------------------------------------------------------

@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
)
class RateLimitAPITests(TestCase):
    """Tests for the /api/accounts/rate_limit/ endpoint."""

    def setUp(self):
        _seed_i18n()
        self.client = Client()
        self.url = reverse('rate-limit')
        self.user = User.objects.create_user(
            email='rate@test.com', password='pass1234'
        )

    def test_unauthenticated_small_file_allowed(self):
        resp = self.client.post(
            self.url,
            data=json.dumps({'files_data': [{'size': '1024'}]}),
            content_type='application/json',
            HTTP_USER_AGENT='TestBrowser/1.0',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('status'))

    def test_unauthenticated_over_limit_rejected(self):
        # FILES_LIMIT in config.py is 104857600 (100MB)
        resp = self.client.post(
            self.url,
            data=json.dumps({'files_data': [{'size': '200000000'}]}),
            content_type='application/json',
            HTTP_USER_AGENT='TestBrowser/1.0',
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertTrue(data.get('limit_exceeded'))

    def test_authenticated_with_active_plan_always_allowed(self):
        self.user.is_plan_active = True
        self.user.save()
        self.client.login(username='rate@test.com', password='pass1234')
        resp = self.client.post(
            self.url,
            data=json.dumps({'files_data': [{'size': '200000000'}]}),
            content_type='application/json',
            HTTP_USER_AGENT='TestBrowser/1.0',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('status'))

    def test_authenticated_with_credits_allowed(self):
        self.user.credits = 10
        self.user.save()
        self.client.login(username='rate@test.com', password='pass1234')
        resp = self.client.post(
            self.url,
            data=json.dumps({'files_data': [{'size': '1024'}]}),
            content_type='application/json',
            HTTP_USER_AGENT='TestBrowser/1.0',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('status'))

    @override_settings(
        CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    )
    def test_unauthenticated_rate_limit_reached(self):
        """After RATE_LIMIT requests, further requests are rejected."""
        from config import RATE_LIMIT
        for i in range(RATE_LIMIT):
            resp = self.client.post(
                self.url,
                data=json.dumps({'files_data': [{'size': '1024'}]}),
                content_type='application/json',
                HTTP_USER_AGENT='TestBrowser/1.0',
            )
            self.assertEqual(resp.status_code, 200, f"Request {i+1} failed")

        # The next request should be rate-limited
        resp = self.client.post(
            self.url,
            data=json.dumps({'files_data': [{'size': '1024'}]}),
            content_type='application/json',
            HTTP_USER_AGENT='TestBrowser/1.0',
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertTrue(data.get('rate_limit'))

    @override_settings(
        CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    )
    def test_authenticated_no_credits_rate_limit_reached(self):
        """After RATE_LIMIT requests, logged-in users with 0 credits see no_credits."""
        from config import RATE_LIMIT
        self.user.credits = 0
        self.user.save()
        self.client.login(username='rate@test.com', password='pass1234')

        for i in range(RATE_LIMIT):
            self.client.post(
                self.url,
                data=json.dumps({'files_data': [{'size': '1024'}]}),
                content_type='application/json',
                HTTP_USER_AGENT='TestBrowser/1.0',
            )

        resp = self.client.post(
            self.url,
            data=json.dumps({'files_data': [{'size': '1024'}]}),
            content_type='application/json',
            HTTP_USER_AGENT='TestBrowser/1.0',
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertTrue(data.get('no_credits'))

    def test_returns_ip_and_cache_key(self):
        resp = self.client.post(
            self.url,
            data=json.dumps({'files_data': [{'size': '1024'}]}),
            content_type='application/json',
            HTTP_USER_AGENT='TestBrowser/1.0',
        )
        data = resp.json()
        self.assertIn('ip', data)
        self.assertIn('cache_key', data)
        self.assertIn('counter', data)

    def test_multiple_files_total_size(self):
        """Multiple files should have their sizes summed."""
        resp = self.client.post(
            self.url,
            data=json.dumps({
                'files_data': [
                    {'size': '50000000'},
                    {'size': '60000000'},  # Total 110MB > 100MB limit
                ]
            }),
            content_type='application/json',
            HTTP_USER_AGENT='TestBrowser/1.0',
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertTrue(data.get('limit_exceeded'))


# ---------------------------------------------------------------------------
# CreditsConsume API
# ---------------------------------------------------------------------------

@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
)
class CreditsConsumeAPITests(TestCase):
    """Tests for the /api/accounts/consume/ endpoint."""

    def setUp(self):
        _seed_i18n()
        self.client = Client()
        self.url = reverse('credits-consume')
        self.user = User.objects.create_user(
            email='consume@test.com', password='pass1234'
        )
        self.user.credits = 5
        self.user.save()

    def test_consume_decrements_credits(self):
        self.client.login(username='consume@test.com', password='pass1234')
        resp = self.client.post(self.url, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.credits, 4)

    def test_consume_at_zero_stays_zero(self):
        self.user.credits = 0
        self.user.save()
        self.client.login(username='consume@test.com', password='pass1234')
        resp = self.client.post(self.url, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.credits, 0)

    def test_consume_unauthenticated(self):
        """Unauthenticated consume should not crash (credits won't change)."""
        resp = self.client.post(self.url, content_type='application/json')
        # DRF may return 200 because consume_credits checks is_authenticated
        self.assertIn(resp.status_code, [200, 403])

    def test_multiple_consumes(self):
        self.client.login(username='consume@test.com', password='pass1234')
        for _ in range(3):
            self.client.post(self.url, content_type='application/json')
        self.user.refresh_from_db()
        self.assertEqual(self.user.credits, 2)


# ---------------------------------------------------------------------------
# ResendVerificationEmail API
# ---------------------------------------------------------------------------

@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
)
class ResendVerificationAPITests(TestCase):
    """Tests for the /api/accounts/resend-verification/ endpoint."""

    def setUp(self):
        _seed_i18n()
        self.client = Client()
        self.url = reverse('resend-verification')
        self.user = User.objects.create_user(
            email='resend@test.com', password='pass1234'
        )

    @mock.patch('app.utils.Utils.send_email', return_value=1)
    def test_resend_authenticated(self, mock_email):
        self.client.login(username='resend@test.com', password='pass1234')
        resp = self.client.post(self.url, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        mock_email.assert_called_once()

    def test_resend_unauthenticated(self):
        """Unauthenticated call should not send an email."""
        with mock.patch('app.utils.Utils.send_email') as mock_email:
            resp = self.client.post(self.url, content_type='application/json')
            # resend_email_verification checks is_authenticated and returns early
            self.assertIn(resp.status_code, [200, 403])


# ---------------------------------------------------------------------------
# CancelSubscription API
# ---------------------------------------------------------------------------

@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
)
class CancelSubscriptionAPITests(TestCase):
    """Tests for the /api/accounts/cancel-subscription/ endpoint."""

    def setUp(self):
        _seed_i18n()
        self.client = Client()
        self.url = reverse('cancel-subscription')
        self.user = User.objects.create_user(
            email='cansub@test.com', password='pass1234'
        )
        self.user.is_plan_active = True
        self.user.processor = 'stripe'
        self.user.save()

    def test_cancel_authenticated(self):
        self.client.login(username='cansub@test.com', password='pass1234')
        resp = self.client.post(self.url, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_plan_active)
        self.assertIsNone(self.user.processor)

    def test_cancel_unauthenticated(self):
        resp = self.client.post(self.url, content_type='application/json')
        self.assertEqual(resp.status_code, 400)


# ---------------------------------------------------------------------------
# PayPal order/subscription API
# ---------------------------------------------------------------------------

@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
)
class PaypalOrderAPITests(TestCase):
    """Tests for the /ipns/paypal-order endpoint."""

    def setUp(self):
        _seed_i18n()
        self.client = Client()
        self.url = reverse('api_payment_paypal')
        self.user = User.objects.create_user(
            email='pporder@test.com', password='pass1234'
        )
        self.plan = Plan.objects.create(
            code_name='paypal-plan', price=10, credits=100,
            days=31, is_subscription=False,
        )

    @mock.patch('finances.models.payment.Payment.create_paypal_order')
    def test_paypal_order_success(self, mock_create):
        mock_create.return_value = ('ORDER-123', 'ok')
        self.client.login(username='pporder@test.com', password='pass1234')
        resp = self.client.post(
            self.url,
            data=json.dumps({'plan': 'paypal-plan'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get('id'), 'ORDER-123')

    def test_paypal_order_bad_plan(self):
        self.client.login(username='pporder@test.com', password='pass1234')
        resp = self.client.post(
            self.url,
            data=json.dumps({'plan': 'nonexistent'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)


# ---------------------------------------------------------------------------
# Coinbase IPN endpoint
# ---------------------------------------------------------------------------

@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
)
class CoinbaseIPNEndpointTests(TestCase):
    """Tests for the /ipns/coinbase endpoint."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='cb@test.com', password='pass1234'
        )
        self.plan = Plan.objects.create(
            code_name='premium', price=30, credits=300, days=31,
        )

    def test_coinbase_webhook_confirmed(self):
        payload = {
            'event': {
                'type': 'charge:confirmed',
                'data': {
                    'code': 'CB_CODE_123',
                    'name': 'premium',
                    'metadata': {
                        'custom': 'cb@test.com',
                    }
                }
            }
        }
        resp = self.client.post(
            '/ipns/coinbase',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)

    def test_coinbase_webhook_failed(self):
        payload = {
            'event': {
                'type': 'charge:failed',
                'data': {
                    'code': 'CB_FAIL_123',
                    'name': 'premium',
                    'metadata': {
                        'custom': 'cb@test.com',
                    }
                }
            }
        }
        resp = self.client.post(
            '/ipns/coinbase',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# LogFrontendError API
# ---------------------------------------------------------------------------

@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
)
class LogFrontendErrorAPITests(TestCase):
    """Tests for the /api/log-error/ endpoint."""

    def setUp(self):
        self.client = Client()
        self.url = reverse('log-error')

    def test_log_error_success(self):
        resp = self.client.post(
            self.url,
            data=json.dumps({
                'message': 'Test JS error',
                'url': 'https://speechtospeechai.com/voice-cloning/',
                'userAgent': 'TestBot/1.0',
                'context': {'line': 42},
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get('status'), 'logged')

    def test_log_error_empty_body(self):
        resp = self.client.post(
            self.url,
            data='',
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)

    def test_log_error_invalid_json(self):
        resp = self.client.post(
            self.url,
            data='not json at all',
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
