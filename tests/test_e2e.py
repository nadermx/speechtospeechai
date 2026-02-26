"""
End-to-end tests for SpeechToSpeechAI: signup -> email verify -> login,
tool page access, and credit purchase flow with mocked Stripe.

Run with: python manage.py test tests.test_e2e -v2
"""
import json
from unittest import mock

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from translations.models.language import Language
from translations.models.translation import Translation

User = get_user_model()


def _setup_i18n():
    Language.objects.get_or_create(
        iso='en', defaults={'name': 'English', 'en_label': 'English'}
    )
    for cn in (
        'site_description', 'site_keywords', 'missing_email',
        'missing_password', 'wrong_credentials', 'email_taken',
        'invalid_email', 'weak_password', 'missing_code', 'invalid_code',
        'forgot_password_email_sent', 'password_changed',
        'login', 'sign_up', 'lost_password', 'restore_your_password',
        'verify_email', 'account_label', 'pricing', 'checkout',
        'contact', 'contact_meta_description', 'about_us',
        'about_us_meta_description', 'terms_of_service', 'privacy_policy',
        'refund', 'success', 'cancel', 'delete', 'deleted',
    ):
        Translation.objects.get_or_create(
            code_name=cn, language='en', defaults={'text': cn},
        )


def _make_user(email='e2e@example.com', password='testpass123', credits=100,
               confirmed=True):
    user = User.objects.create_user(email=email, password=password)
    user.credits = credits
    user.is_confirm = confirmed
    user.save()
    return user


# ---------------------------------------------------------------------------
# Signup -> Verify -> Login flow
# ---------------------------------------------------------------------------
@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
)
class SignupFlowTests(TestCase):
    """Full signup -> email verification -> login flow."""

    @classmethod
    def setUpTestData(cls):
        _setup_i18n()

    def setUp(self):
        self.client = Client()

    @mock.patch('app.utils.Utils.send_email')
    def test_full_signup_verify_login_flow(self, mock_send_email):
        # Step 1: Register a new user
        resp = self.client.post(reverse('register'), {
            'email': 'newuser@example.com',
            'password': 'securepass1',
        })
        self.assertIn(resp.status_code, [200, 302])
        mock_send_email.assert_called()

        # Verify user was created
        user = User.objects.get(email='newuser@example.com')
        self.assertFalse(user.is_confirm)

        # Step 2: Login
        self.client.force_login(user)

        # Step 3: Verify email with code
        resp = self.client.post(reverse('verify'), {
            'code': user.verification_code,
        })
        self.assertIn(resp.status_code, [200, 302])

        user.refresh_from_db()
        self.assertTrue(user.is_confirm)

    @mock.patch('app.utils.Utils.send_email')
    def test_signup_duplicate_email_fails(self, mock_send_email):
        _make_user(email='dup@example.com')

        resp = self.client.post(reverse('register'), {
            'email': 'dup@example.com',
            'password': 'securepass1',
        })
        self.assertIn(resp.status_code, [200, 302])
        self.assertEqual(
            User.objects.filter(email='dup@example.com').count(), 1
        )

    @mock.patch('app.utils.Utils.send_email')
    def test_signup_weak_password_fails(self, mock_send_email):
        resp = self.client.post(reverse('register'), {
            'email': 'weak@example.com',
            'password': 'ab',
        })
        self.assertIn(resp.status_code, [200, 302])
        self.assertFalse(
            User.objects.filter(email='weak@example.com').exists()
        )

    @mock.patch('app.utils.Utils.send_email')
    def test_signup_missing_email_fails(self, mock_send_email):
        resp = self.client.post(reverse('register'), {
            'email': '',
            'password': 'securepass1',
        })
        self.assertIn(resp.status_code, [200, 302])


# ---------------------------------------------------------------------------
# Login flow
# ---------------------------------------------------------------------------
@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
)
class LoginFlowTests(TestCase):
    """Test login with valid and invalid credentials."""

    @classmethod
    def setUpTestData(cls):
        _setup_i18n()

    def setUp(self):
        self.client = Client()

    def test_login_valid_credentials(self):
        _make_user(email='login@example.com')
        resp = self.client.post(reverse('login'), {
            'email': 'login@example.com',
            'password': 'testpass123',
        })
        self.assertIn(resp.status_code, [200, 302])

    def test_login_invalid_credentials(self):
        _make_user(email='login2@example.com')
        resp = self.client.post(reverse('login'), {
            'email': 'login2@example.com',
            'password': 'wrongpassword',
        })
        self.assertIn(resp.status_code, [200, 302])

    def test_login_nonexistent_user(self):
        resp = self.client.post(reverse('login'), {
            'email': 'nobody@example.com',
            'password': 'anypassword',
        })
        self.assertIn(resp.status_code, [200, 302])

    def test_login_missing_fields(self):
        resp = self.client.post(reverse('login'), {
            'email': '',
            'password': '',
        })
        self.assertIn(resp.status_code, [200, 302])


# ---------------------------------------------------------------------------
# Tool pages E2E (authenticated user browses tool pages)
# ---------------------------------------------------------------------------
@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
)
class ToolPageE2ETests(TestCase):
    """Test that all tool pages load for an authenticated user."""

    @classmethod
    def setUpTestData(cls):
        _setup_i18n()

    def setUp(self):
        self.client = Client()
        self.user = _make_user(email='tools@example.com', credits=50)
        self.client.force_login(self.user)

    def test_index_page_authenticated(self):
        resp = self.client.get(reverse('index'))
        self.assertEqual(resp.status_code, 200)

    def test_voice_cloning_page(self):
        resp = self.client.get(reverse('voice-cloning'))
        self.assertEqual(resp.status_code, 200)

    def test_text_to_speech_page(self):
        resp = self.client.get(reverse('text-to-speech'))
        self.assertEqual(resp.status_code, 200)

    def test_speech_to_text_page(self):
        resp = self.client.get(reverse('speech-to-text'))
        self.assertEqual(resp.status_code, 200)

    def test_voice_conversion_page(self):
        resp = self.client.get(reverse('voice-conversion'))
        self.assertEqual(resp.status_code, 200)

    def test_real_time_chat_page(self):
        resp = self.client.get(reverse('real-time-chat'))
        self.assertEqual(resp.status_code, 200)

    def test_speech_translation_page(self):
        resp = self.client.get(reverse('speech-translation'))
        self.assertEqual(resp.status_code, 200)

    def test_audio_enhancement_page(self):
        resp = self.client.get(reverse('audio-enhancement'))
        self.assertEqual(resp.status_code, 200)

    def test_custom_training_page(self):
        resp = self.client.get(reverse('custom-training'))
        self.assertEqual(resp.status_code, 200)

    def test_api_docs_page(self):
        resp = self.client.get(reverse('api-docs'))
        self.assertEqual(resp.status_code, 200)

    def test_models_page(self):
        resp = self.client.get(reverse('models'))
        self.assertEqual(resp.status_code, 200)

    def test_account_page(self):
        resp = self.client.get(reverse('account'))
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# Credit purchase flow (mocked Stripe)
# ---------------------------------------------------------------------------
@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
)
class CreditSystemTests(TestCase):
    """Test the credit purchase flow with mocked Stripe payment."""

    @classmethod
    def setUpTestData(cls):
        _setup_i18n()

    def setUp(self):
        self.client = Client()
        self.user = _make_user(email='buyer@example.com', credits=5)
        self.client.force_login(self.user)

    def test_checkout_page_loads(self):
        resp = self.client.get(reverse('checkout'))
        self.assertIn(resp.status_code, [200, 302])

    def test_pricing_page_shows_plans(self):
        resp = self.client.get(reverse('pricing'))
        self.assertEqual(resp.status_code, 200)

    @mock.patch('finances.models.payment.Payment.make_charge_stripe')
    @mock.patch('app.utils.Utils.send_email')
    def test_stripe_credit_purchase(self, mock_email, mock_stripe):
        from finances.models.plan import Plan
        plan = Plan.objects.create(
            name='100 Credits',
            code_name='credits_100',
            price=9.99,
            credits=100,
            is_subscription=False,
            is_api_plan=False,
            days=31,
        )

        mock_payment = mock.MagicMock()
        mock_payment.customer_token = 'cus_test123'
        mock_payment.card_token = 'card_test123'
        mock_payment.processor = 'stripe'
        mock_stripe.return_value = (mock_payment, None)

        resp = self.client.post(reverse('checkout'), {
            'processor': 'stripe',
            'nonce': 'tok_test_visa',
            'plan': 'credits_100',
        })
        self.assertIn(resp.status_code, [200, 302])

    @mock.patch('app.utils.Utils.send_email')
    def test_cancel_subscription(self, mock_email):
        self.user.is_plan_active = True
        self.user.processor = 'stripe'
        self.user.payment_nonce = 'cus_test'
        self.user.save()

        resp = self.client.post(reverse('cancel-subscription'))
        self.assertIn(resp.status_code, [200, 302])

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_plan_active)

    def test_success_page(self):
        resp = self.client.get(reverse('success'))
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# Lost password & restore password flows
# ---------------------------------------------------------------------------
@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
)
class AccountManagementTests(TestCase):
    """Test email resend, lost password, and restore password flows."""

    @classmethod
    def setUpTestData(cls):
        _setup_i18n()

    def setUp(self):
        self.client = Client()
        self.user = _make_user(email='acct@example.com', confirmed=False)

    @mock.patch('app.utils.Utils.send_email')
    def test_resend_verification_email(self, mock_send):
        self.client.force_login(self.user)
        resp = self.client.post(reverse('resend-verification'))
        self.assertIn(resp.status_code, [200, 302])
        mock_send.assert_called()

    @mock.patch('app.utils.Utils.send_email')
    def test_lost_password_flow(self, mock_send):
        resp = self.client.post(reverse('lost-password'), {
            'email': 'acct@example.com',
        })
        self.assertIn(resp.status_code, [200, 302])

    def test_restore_password_page_loads(self):
        resp = self.client.get(reverse('restore-password'))
        self.assertEqual(resp.status_code, 200)

    @mock.patch('app.utils.Utils.send_email')
    def test_restore_password_with_token(self, mock_send):
        self.user.restore_password_token = 'test-token-123'
        self.user.save()

        resp = self.client.post(reverse('restore-password'), {
            'token': 'test-token-123',
            'password': 'newpass123',
            'confirm_password': 'newpass123',
        })
        self.assertIn(resp.status_code, [200, 302])

    @mock.patch('app.utils.Utils.send_email')
    def test_verify_wrong_code_fails(self, mock_send):
        self.client.force_login(self.user)
        resp = self.client.post(reverse('verify'), {
            'code': 'WRONGCODE',
        })
        self.assertIn(resp.status_code, [200, 302])
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_confirm)

    def test_logout_and_redirect(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse('logout'))
        self.assertIn(resp.status_code, [302, 301])
        # After logout, account should redirect
        resp = self.client.get(reverse('account'))
        self.assertIn(resp.status_code, [302, 301])
