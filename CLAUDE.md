# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Speech to Speech AI - A comprehensive speech AI platform featuring voice cloning, TTS, STT, voice conversion, and real-time conversational AI. Built on Django with a separate GPU API server for processing.

**Live**: https://speechtospeechai.com | **API**: https://api.speechtospeechai.com
**Server**: 167.172.17.40 (DigitalOcean) | **Deploy path**: /home/www/speechtospeechai | **ansible_user**: root

## Build & Run Commands

```bash
# Development
python manage.py runserver
python manage.py migrate
python manage.py createsuperuser

# Database setup
python manage.py set_languages      # Load languages from JSON
python manage.py set_plans          # Load pricing plans
python manage.py set_text_backup    # Load TextBase entries from translations/json/textbase.json

# Other management commands
python manage.py rebill               # Process recurring billing
python manage.py expire_pro_users     # Expire lapsed subscriptions
python manage.py remove_pro_for_old_plans  # Remove pro status from old plan users
python manage.py up_users_backup      # Restore users from accounts/json/users.json
python manage.py create_paypal_product # Create PayPal product catalog
python manage.py create_paypal_plans  # Create PayPal billing plans
python manage.py run_translation      # Auto-translate UI text
python manage.py delete_translations  # Clean orphaned UI translations

# Static files (production)
python manage.py collectstatic --noinput

# Deployment (NO gitpull.yml — use manual deploy via SSH)
ssh root@167.172.17.40 "cd /home/www/speechtospeechai && git pull && source venv/bin/activate && pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput && supervisorctl restart speechtospeechai"

# Or via Ansible ad-hoc:
ansible -i ansible/servers all -m shell -a "cd /home/www/speechtospeechai && git pull https://nadermx:TOKEN@github.com/nadermx/speechtospeechai.git main && supervisorctl restart speechtospeechai"

# Full server setup (first time only)
cd ansible && ansible-playbook -i servers djangodeployubuntu20.yml
```

## Architecture

### Two-Server Architecture
- **Web Server** (167.172.17.40): Django frontend, user auth, payments
- **GPU Server** (38.248.6.142): Speech AI processing via api.imageeditor.ai

### Django Apps
- `accounts/` - Custom email-based user model with credits system
- `core/` - Main views and page routing (all tool pages)
- `finances/` - Payment processing (Stripe, PayPal, Square, Coinbase)
- `translations/` - Database-driven i18n (not Django's built-in)
- `contact_messages/` - Contact form handling

### Key Files
- `config.py` - Environment configuration (git-ignored, contains credentials)
- `accounts/views.py:GlobalVars` - Template context provider (lang, i18n, api_server)
- `static/js/speech-api.js` - JavaScript API client for all speech endpoints

### Translation System
Uses custom database-driven translations, not Django i18n:
```html
{{ g.i18n.your_code_name|default:"Fallback text" }}
```

## API Integration

Frontend calls GPU server for processing. JavaScript client in `static/js/speech-api.js`:

```javascript
// Text-to-Speech
const result = await SpeechAPI.textToSpeech(text, {model: 'xtts-v2', language: 'en'});

// Voice Cloning
const result = await SpeechAPI.voiceClone(audioFile, text, {language: 'en'});

// Poll for results
const final = await SpeechAPI.pollResults(result.uuid);
```

API endpoints (on api.speechtospeechai.com or api.imageeditor.ai):
- `POST /v1/tts/` - Text-to-Speech
- `POST /v1/voice-clone/` - Voice Cloning
- `POST /v1/voice-convert/` - Voice Conversion
- `POST /v1/speech-translate/` - Speech Translation
- `POST /v1/audio-enhance/` - Audio Enhancement
- `GET /v1/speech/results/?uuid=` - Check job status

## Credit System

| Feature | Credits |
|---------|---------|
| Voice Cloning | 1 per clone |
| Text to Speech | 1 per 1000 chars |
| Speech to Text | 1 per minute |
| Voice Conversion | 2 per minute |
| Speech Translation | 3 per minute |
| Audio Enhancement | 1 per minute |

## Server Access

```bash
# Web server
ssh root@167.172.17.40

# API server (requires password: see ansible/group_vars/all)
sshpass -p 'PASSWORD' ssh imageeditor@38.248.6.142

# Logs
tail -f /var/log/speechtospeechai/speechtospeechai.err.log

# Database
sudo -u postgres psql speechtospeechai
```

## GPU Server Package Status

The shared GPU server (38.248.6.142 / api.imageeditor.ai) has these TTS packages installed:

### venv312 (Primary, Python 3.12)
kokoro, chatterbox-tts, melotts, faster-whisper, funasr, demucs, librosa, suno-bark, piper-tts, openvoice, parler-tts, tortoise-tts, noisereduce

### venv311 (Coqui TTS, Python 3.11)
TTS 0.22.0 (Coqui TTS) - XTTS-v2/VITS only. Called via subprocess (`converter/coqui_tts_helper.py`) because Coqui TTS requires Python <3.12.

### Cloned Model Repos (`/home/www/api/models/`)
GPT-SoVITS, CosyVoice2, IndexTTS2, SparkTTS

### Gated Models (not yet available)
Higgs-v2, GLM-TTS, Sesame CSM - need HuggingFace token + access approval

## Deployment Notes

- Use Ansible for server operations per global CLAUDE.md
- **No gitpull.yml** — deploy manually via SSH or Ansible ad-hoc commands
- **ansible_user is root** — `disableroot.yml` exists but was never run; consider running it to create a dedicated deploy user
- `config.py` and `ansible/servers` are git-ignored - copy manually to server
- Run migrations on server, not locally (files in .gitignore)
- DNS nameservers must point to DigitalOcean (ns1/ns2/ns3.digitalocean.com)
