# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Speech to Speech AI - A comprehensive speech AI platform featuring voice cloning, TTS, STT, voice conversion, and real-time conversational AI. Built on Django with a separate GPU API server for processing.

**Live**: https://speechtospeechai.com | **API**: https://api.speechtospeechai.com

## Build & Run Commands

```bash
# Development
python manage.py runserver
python manage.py migrate
python manage.py createsuperuser

# Database setup
python manage.py set_languages      # Load languages from JSON
python manage.py set_plans          # Load pricing plans

# Static files (production)
python manage.py collectstatic --noinput

# Deployment (from local machine)
cd ansible && ansible-playbook -i servers djangodeployubuntu20.yml

# Quick deploy via SSH
ssh root@167.172.17.40 "cd /home/www/speechtospeechai && git pull && source venv/bin/activate && pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput && supervisorctl restart speechtospeechai"
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

## Deployment Notes

- Use Ansible for server operations per global CLAUDE.md
- `config.py` and `ansible/servers` are git-ignored - copy manually to server
- Run migrations on server, not locally (files in .gitignore)
- DNS nameservers must point to DigitalOcean (ns1/ns2/ns3.digitalocean.com)
