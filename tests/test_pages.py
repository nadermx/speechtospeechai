"""
Tests for all page loads -- every URL defined in core/urls.py.

Ensures every page renders without server errors and returns the correct
HTTP status code.  Checks public pages, auth-gated pages, and
tool-specific content pages.

Run with: python manage.py test tests.test_pages -v2
"""
from unittest import mock

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from finances.models.plan import Plan
from translations.models.language import Language
from translations.models.translation import Translation

User = get_user_model()


def _seed_i18n():
    """Seed the minimum Language + Translation data required by all views."""
    Language.objects.get_or_create(
        iso='en', defaults={'name': 'English', 'en_label': 'English'}
    )
    keys = [
        'login', 'sign_up', 'lost_password', 'restore_your_password',
        'verify_email', 'account_label', 'pricing', 'checkout',
        'success', 'contact', 'about_us', 'terms_of_service',
        'privacy_policy', 'refund', 'cancel', 'delete', 'deleted',
        'site_description', 'contact_meta_description',
        'about_us_meta_description',
    ]
    for key in keys:
        Translation.objects.get_or_create(
            code_name=key, language='en', defaults={'text': key}
        )


# ---------------------------------------------------------------------------
# Public pages (no auth required)
# ---------------------------------------------------------------------------

@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
)
class PublicPageTests(TestCase):
    """Every public page should return 200 for anonymous users."""

    def setUp(self):
        _seed_i18n()
        self.client = Client()

    def test_index_page(self):
        resp = self.client.get(reverse('index'))
        self.assertEqual(resp.status_code, 200)

    def test_login_page(self):
        resp = self.client.get(reverse('login'))
        self.assertEqual(resp.status_code, 200)

    def test_register_page(self):
        resp = self.client.get(reverse('register'))
        self.assertEqual(resp.status_code, 200)

    def test_lost_password_page(self):
        resp = self.client.get(reverse('lost-password'))
        self.assertEqual(resp.status_code, 200)

    def test_pricing_page(self):
        resp = self.client.get(reverse('pricing'))
        self.assertEqual(resp.status_code, 200)

    def test_about_page(self):
        resp = self.client.get(reverse('about'))
        self.assertEqual(resp.status_code, 200)

    def test_contact_page(self):
        resp = self.client.get(reverse('contact'))
        self.assertEqual(resp.status_code, 200)

    def test_terms_page(self):
        resp = self.client.get(reverse('terms'))
        self.assertEqual(resp.status_code, 200)

    def test_privacy_page(self):
        resp = self.client.get(reverse('privacy'))
        self.assertEqual(resp.status_code, 200)

    def test_refund_page(self):
        resp = self.client.get(reverse('refund'))
        self.assertEqual(resp.status_code, 200)

    def test_success_page(self):
        resp = self.client.get(reverse('success'))
        self.assertEqual(resp.status_code, 200)

    # Tool pages
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


# ---------------------------------------------------------------------------
# Auth-gated pages (require login or verification)
# ---------------------------------------------------------------------------

@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
)
class AuthGatedPageTests(TestCase):
    """Pages that require authentication should redirect anonymous users."""

    def setUp(self):
        _seed_i18n()
        self.client = Client()

    def test_account_redirects_to_login(self):
        resp = self.client.get(reverse('account'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('login', resp.url)

    def test_verify_redirects_unauthenticated(self):
        resp = self.client.get(reverse('verify'))
        self.assertEqual(resp.status_code, 302)

    def test_checkout_redirects_unauthenticated(self):
        resp = self.client.get(reverse('checkout'))
        self.assertEqual(resp.status_code, 302)

    def test_cancel_redirects_unauthenticated(self):
        resp = self.client.get(reverse('cancel'))
        self.assertEqual(resp.status_code, 302)

    def test_delete_redirects_unauthenticated(self):
        resp = self.client.get(reverse('delete'))
        self.assertEqual(resp.status_code, 302)


@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
)
class VerifiedUserPageTests(TestCase):
    """Pages for verified (is_confirm=True) logged-in users."""

    def setUp(self):
        _seed_i18n()
        self.client = Client()
        self.user = User.objects.create_user(
            email='verified@test.com', password='pass1234',
        )
        self.user.is_confirm = True
        self.user.save()
        self.client.login(username='verified@test.com', password='pass1234')

    def test_account_page(self):
        resp = self.client.get(reverse('account'))
        self.assertEqual(resp.status_code, 200)

    def test_cancel_page(self):
        resp = self.client.get(reverse('cancel'))
        self.assertEqual(resp.status_code, 200)

    def test_delete_page(self):
        resp = self.client.get(reverse('delete'))
        self.assertEqual(resp.status_code, 200)

    def test_checkout_requires_plan(self):
        # Checkout without plan param redirects to pricing
        resp = self.client.get(reverse('checkout'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('pricing', resp.url)

    def test_checkout_with_valid_plan(self):
        plan = Plan.objects.create(
            code_name='test-plan', price=10, credits=100, days=31,
        )
        resp = self.client.get(reverse('checkout') + '?plan=test-plan')
        self.assertEqual(resp.status_code, 200)

    def test_checkout_with_invalid_plan(self):
        resp = self.client.get(reverse('checkout') + '?plan=nonexistent')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('pricing', resp.url)


@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
)
class UnverifiedUserPageTests(TestCase):
    """Unverified users should be redirected to the verify page from certain pages."""

    def setUp(self):
        _seed_i18n()
        self.client = Client()
        self.user = User.objects.create_user(
            email='unverified@test.com', password='pass1234',
        )
        # is_confirm is False by default
        self.client.login(username='unverified@test.com', password='pass1234')

    def test_account_redirects_to_verify(self):
        resp = self.client.get(reverse('account'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('verify', resp.url)

    def test_checkout_redirects_to_verify(self):
        Plan.objects.create(code_name='vfy-plan', price=5, credits=50, days=31)
        resp = self.client.get(reverse('checkout') + '?plan=vfy-plan')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('verify', resp.url)

    def test_verify_page_accessible(self):
        resp = self.client.get(reverse('verify'))
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# Authenticated user cannot see login/register/lost-password
# ---------------------------------------------------------------------------

@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
)
class AuthenticatedRedirectTests(TestCase):
    """Authenticated users should be redirected away from auth pages."""

    def setUp(self):
        _seed_i18n()
        self.client = Client()
        self.user = User.objects.create_user(
            email='auth@test.com', password='pass1234'
        )
        self.client.login(username='auth@test.com', password='pass1234')

    def test_login_redirects(self):
        resp = self.client.get(reverse('login'))
        self.assertEqual(resp.status_code, 302)

    def test_register_redirects(self):
        resp = self.client.get(reverse('register'))
        self.assertEqual(resp.status_code, 302)

    def test_lost_password_redirects(self):
        resp = self.client.get(reverse('lost-password'))
        self.assertEqual(resp.status_code, 302)


# ---------------------------------------------------------------------------
# Pricing page shows plans
# ---------------------------------------------------------------------------

@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
)
class PricingPageContentTests(TestCase):
    """The pricing page should list available plans."""

    def setUp(self):
        _seed_i18n()
        self.client = Client()
        Plan.objects.create(code_name='basic', price=5, credits=50, days=31)
        Plan.objects.create(code_name='pro', price=15, credits=200, days=31)

    def test_plans_in_context(self):
        resp = self.client.get(reverse('pricing'))
        self.assertEqual(resp.status_code, 200)
        plans = resp.context.get('plans')
        self.assertIsNotNone(plans)
        self.assertEqual(plans.count(), 2)

    def test_plans_ordered_by_price(self):
        resp = self.client.get(reverse('pricing'))
        plans = list(resp.context['plans'])
        self.assertEqual(plans[0].code_name, 'basic')
        self.assertEqual(plans[1].code_name, 'pro')

    def test_current_plan_none_for_anonymous(self):
        resp = self.client.get(reverse('pricing'))
        self.assertIsNone(resp.context.get('current_plan'))


# ---------------------------------------------------------------------------
# Restore-password page
# ---------------------------------------------------------------------------

@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
)
class RestorePasswordPageTests(TestCase):
    """Tests for the restore-password page."""

    def setUp(self):
        _seed_i18n()
        self.client = Client()

    def test_no_token_unauthenticated_redirects(self):
        resp = self.client.get(reverse('restore-password'))
        self.assertEqual(resp.status_code, 302)

    def test_with_token_renders(self):
        resp = self.client.get(reverse('restore-password') + '?token=abcdef')
        self.assertEqual(resp.status_code, 200)

    def test_authenticated_generates_token(self):
        user = User.objects.create_user(email='rp@test.com', password='pass1234')
        self.client.login(username='rp@test.com', password='pass1234')
        resp = self.client.get(reverse('restore-password'))
        self.assertEqual(resp.status_code, 200)
        # Should have a token in the context
        self.assertIsNotNone(resp.context.get('token'))


# ---------------------------------------------------------------------------
# Contact form
# ---------------------------------------------------------------------------

@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
)
class ContactPageTests(TestCase):
    """Tests for the contact page and form."""

    def setUp(self):
        _seed_i18n()
        self.client = Client()

    def test_contact_has_captcha(self):
        resp = self.client.get(reverse('contact'))
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        self.assertIn('captcha', content.lower())

    def test_contact_post_invalid_captcha(self):
        resp = self.client.post(reverse('contact'), {
            'email': 'test@test.com',
            'message': 'Hello!',
            'captcha_0': 'test',
            'captcha_1': 'wrong',
        })
        self.assertEqual(resp.status_code, 200)
        # Should stay on page with error

    def test_contact_form_context_has_form(self):
        resp = self.client.get(reverse('contact'))
        self.assertIn('form', resp.context)


# ---------------------------------------------------------------------------
# Refund page
# ---------------------------------------------------------------------------

@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
)
class RefundPageTests(TestCase):
    """Tests for the refund page."""

    def setUp(self):
        _seed_i18n()
        self.client = Client()

    def test_refund_page_get(self):
        resp = self.client.get(reverse('refund'))
        self.assertEqual(resp.status_code, 200)

    def test_refund_post_missing_fields(self):
        resp = self.client.post(reverse('refund'), {
            'transaction_id': '',
            'email_refund': '',
        })
        self.assertEqual(resp.status_code, 200)
        # Should stay on page with errors


# ---------------------------------------------------------------------------
# Favicon and ads.txt
# ---------------------------------------------------------------------------

@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
)
class MiscURLTests(TestCase):
    """Tests for misc URLs like favicon and ads.txt."""

    def setUp(self):
        self.client = Client()

    def test_favicon_redirects(self):
        resp = self.client.get('/favicon.ico')
        self.assertEqual(resp.status_code, 301)  # permanent redirect

    def test_ads_txt(self):
        resp = self.client.get('/ads.txt')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/plain')


# ---------------------------------------------------------------------------
# Language switching
# ---------------------------------------------------------------------------

@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
)
class LanguageSwitchTests(TestCase):
    """Test that ?lang= parameter is respected."""

    def setUp(self):
        _seed_i18n()
        # Also add Spanish
        Language.objects.get_or_create(
            iso='es', defaults={'name': 'Espanol', 'en_label': 'Spanish'}
        )
        Translation.objects.get_or_create(
            code_name='site_description', language='es',
            defaults={'text': 'Descripcion del sitio'}
        )
        self.client = Client()

    def test_default_language_english(self):
        resp = self.client.get(reverse('index'))
        self.assertEqual(resp.status_code, 200)
        settings = resp.context.get('g')
        self.assertEqual(settings['lang'].iso, 'en')

    def test_switch_to_spanish(self):
        resp = self.client.get(reverse('index') + '?lang=es')
        self.assertEqual(resp.status_code, 200)
        settings = resp.context.get('g')
        self.assertEqual(settings['lang'].iso, 'es')

    def test_invalid_lang_falls_back_to_english(self):
        resp = self.client.get(reverse('index') + '?lang=zz')
        self.assertEqual(resp.status_code, 200)
        settings = resp.context.get('g')
        self.assertEqual(settings['lang'].iso, 'en')

    def test_language_persists_in_session(self):
        self.client.get(reverse('index') + '?lang=es')
        # Second request without ?lang should still be Spanish
        resp = self.client.get(reverse('index'))
        settings = resp.context.get('g')
        self.assertEqual(settings['lang'].iso, 'es')


# ---------------------------------------------------------------------------
# Account page context
# ---------------------------------------------------------------------------

@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db',
)
class AccountPageContextTests(TestCase):
    """Test that the account page provides the right context variables."""

    def setUp(self):
        _seed_i18n()
        self.client = Client()
        self.user = User.objects.create_user(
            email='ctx@test.com', password='pass1234',
        )
        self.user.is_confirm = True
        self.user.credits = 42
        self.user.save()
        self.client.login(username='ctx@test.com', password='pass1234')

    def test_credits_in_context(self):
        resp = self.client.get(reverse('account'))
        self.assertEqual(resp.context['credits'], 42)

    def test_payments_in_context(self):
        resp = self.client.get(reverse('account'))
        self.assertIn('payments', resp.context)

    def test_plan_subscribed_none_default(self):
        resp = self.client.get(reverse('account'))
        self.assertIsNone(resp.context.get('plan_subscribed'))

    def test_plan_subscribed_found(self):
        plan = Plan.objects.create(
            code_name='ctx-plan', price=10, credits=100, days=31,
        )
        self.user.plan_subscribed = 'ctx-plan'
        self.user.save()
        resp = self.client.get(reverse('account'))
        self.assertEqual(resp.context['plan_subscribed'].code_name, 'ctx-plan')
