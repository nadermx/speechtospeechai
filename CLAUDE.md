# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DjangoBase is a reusable Django 5.x project template with built-in user authentication, credits-based billing, multi-processor payments (Stripe, PayPal, Square, Coinbase), and a custom database-driven translation system. It's designed to be cloned and customized for new SaaS projects.

## Common Commands

```bash
# Development
python manage.py runserver
python manage.py migrate
python manage.py createsuperuser

# Translations
python manage.py set_languages      # Load languages from JSON
python manage.py run_translation    # Auto-translate via Google Translate API

# Plans
python manage.py set_plans          # Load plans from finances/json/plans.json

# PayPal Setup (if using subscriptions)
python manage.py create_paypal_product
python manage.py create_paypal_plans

# Subscription Management (run via cron)
python manage.py rebill             # Daily billing for subscriptions
python manage.py expire_pro_users   # Deactivate expired subscriptions

# Run tests
python manage.py test
python manage.py test accounts      # Single app
```

## Quick Start for New Projects

```bash
python customize.py           # Interactive setup script
cp config_example.py config.py  # If not using customize.py
pip install -r requirements.txt
python manage.py migrate
python manage.py set_languages
python manage.py runserver
```

See `SETUP.md` for detailed customization instructions.

## Architecture

### Configuration
Settings split between `app/settings.py` (Django defaults) and `config.py` (secrets/env-specific). The `config.py` is gitignored - copy from `config_example.py` or use `customize.py`.

Key config values:
- `PROJECT_NAME` - Used in templates and emails
- `PROJECT_DOMAIN` - Your domain for email sending
- `ROOT_DOMAIN` - Full URL (e.g., https://myapp.com)
- `PROCESSORS` - List of enabled payment processors: `['stripe', 'paypal']`

### Custom Translation System
**Not Django's built-in i18n.** Uses three models in `translations/`:
- `Language` - available languages (populated via `set_languages` command)
- `TextBase` - source text entries with `code_name` identifier
- `Translation` - translated text per language

Usage in views: `Translation.get_text_by_lang('en')` returns dict of `{code_name: text}`. Add new text via admin at `Translations > Text bases`, then run `python manage.py run_translation`.

### User & Authentication
Custom user model `accounts.CustomUser` (single file at `accounts/models.py`) with:
- Email as username (`USERNAME_FIELD = "email"`)
- Credits system for usage-based billing
- Subscription tracking (`is_plan_active`, `next_billing_date`, `plan_subscribed`)
- Payment processor tokens (`payment_nonce`, `card_nonce`, `processor`)
- 6-digit email verification codes (`verification_code`)
- API token for external authentication

User model contains most business logic as static methods: `register_user()`, `login_user()`, `upgrade_account()`, `cancel_subscription()`, etc.

### Email System
Uses `Utils.send_email()` from `app/utils.py` with Django's native SMTP backend. See `EMAIL_SETUP.md` for DNS configuration.

Email templates in `templates/mailing/` use `{{ project_name }}` and `{{ root_domain }}` variables.

For development, set in `config.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Payment Processing
`finances/` supports Stripe, Square, PayPal, Coinbase. Plans defined in `finances/json/plans.json` or admin.

Key models:
- `Plan` (`finances/models/plan.py`) - pricing, credits granted, subscription length, processor keys
- `Payment` (`finances/models/payment.py`) - transactions with status (pending/success/failed/refunded)

Payment methods are static on `Payment`: `make_charge_stripe()`, `make_charge_square()`, `make_charge_paypal()`.

Webhooks at `/ipns/paypal` and `/ipns/coinbase`.

### View Pattern
All views call `GlobalVars.get_globals(request)` from `accounts/views.py` to build context:
```python
settings = GlobalVars.get_globals(request)
# Returns: {'lang': Language, 'i18n': {code_name: text}, 'languages': [...], 'scripts_version': str}
```
Templates receive this as `g` context variable (e.g., `{{ g.i18n.welcome_title }}`).

Views are class-based in `core/views.py`. Most authentication/payment logic is delegated to `CustomUser` model methods.

### API Endpoints
REST Framework views in `accounts/views.py` (not a separate api_views.py):
- `/api/accounts/rate_limit/` - Check usage quotas per IP
- `/api/accounts/consume/` - Decrement credits after API usage
- `/api/accounts/resend-verification/` - Resend email verification
- `/api/accounts/cancel-subscription/` - Cancel active subscription

### Frontend
- Bootstrap 5 (loaded via CDN)
- Custom styles in `static/css/styles.css`
- Language selector in navbar with `?lang=` URL parameter


## Key Patterns

### Method Return Convention
Methods return `(object, error)` tuples - check first element for success:
```python
payment, errors = Payment.make_charge_stripe(user, token, amount, settings)
if errors:
    # handle error
```
This pattern is used throughout: `CustomUser.register_user()`, `Payment.make_refund()`, `Message.save_message()`, etc.

### Adding New Translations
1. Add TextBase entry in admin (`Translations > Text bases`) with unique `code_name`
2. Run `python manage.py run_translation` to auto-translate via Google API
3. Access in templates: `{{ g.i18n.your_code_name|default:"Fallback" }}`

### Rate Limiting
- API rate limiting in `RateLimit` view uses IP+User-Agent hash stored in Redis
- Payment rate limiting in `CustomUser.payment_ratelimited()` - max 3 attempts per hour
- Authenticated users with active plans or credits bypass limits

### Caching
Uses Django-Redis. Cache helpers in `app/utils.py`:
- `Utils.get_from_cache(key)` / `Utils.set_to_cache(key, value, exp)`
- Languages are cached globally in `GlobalVars.get_globals()`

## Deployment

Ansible playbooks in `ansible/`:
```bash
cd ansible
ansible-playbook -i servers gitpull.yml           # Deploy updates
ansible-playbook -i servers djangodeployubuntu20.yml  # Full deploy
```

Copy and configure before first deploy:
- `ansible/servers.example` → `ansible/servers`
- `ansible/group_vars/all.example` → `ansible/group_vars/all`
