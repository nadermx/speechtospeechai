# Speech to Speech AI

The most comprehensive open-source speech AI platform, featuring voice cloning, text-to-speech, speech-to-text, voice conversion, and real-time conversational AI.

**Live Site**: https://speechtospeechai.com
**GitHub**: https://github.com/nadermx/speechtospeechai
**API Docs**: https://speechtospeechai.com/api-docs/

## Tech Stack

- **Backend**: Django 5.1, PostgreSQL, Redis
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Payments**: Stripe (primary), PayPal, Coinbase
- **AI Models**: PersonaPlex 7B, Fish Speech v1.5, Orpheus TTS, Whisper Large v3, OpenVoice v2
- **API Server**: api.imageeditor.ai (GPU processing)

## Project Structure

```
speechtospeechai/
├── accounts/           # User authentication, credits, subscriptions
├── app/               # Django settings, main URLs
├── core/              # Main views and page routing
├── finances/          # Payment processing (Stripe, PayPal, etc.)
├── translations/      # Database-driven i18n system
├── contact_messages/  # Contact form handling
├── templates/         # All HTML templates
│   ├── base.html              # Main layout with nav
│   ├── index.html             # Landing page
│   ├── voice-cloning.html     # Voice cloning tool
│   ├── text-to-speech.html    # TTS tool
│   ├── speech-to-text.html    # STT tool
│   ├── voice-conversion.html  # Voice conversion
│   ├── real-time-chat.html    # PersonaPlex chat
│   ├── speech-translation.html# Speech translation
│   ├── audio-enhancement.html # Audio cleanup
│   ├── custom-training.html   # Custom model training
│   ├── api-docs.html          # API documentation
│   ├── models.html            # AI models info
│   ├── pricing.html           # Pricing page
│   └── ...                    # Auth, legal pages
├── static/
│   ├── css/styles.css
│   └── js/utils.js
├── ansible/           # Deployment automation
├── config.py          # Environment configuration (git-ignored)
└── requirements.txt
```

## Common Commands

```bash
# Development
python manage.py runserver
python manage.py migrate
python manage.py createsuperuser

# Setup
python manage.py set_languages      # Load languages
python manage.py set_plans          # Load pricing plans

# Deployment
cd ansible && ansible-playbook -i servers djangodeployubuntu20.yml
```

## Key Features

1. **Voice Cloning** - Clone any voice from 10-30 seconds of audio
2. **Text to Speech** - 50+ voices, 29 languages, emotion control
3. **Speech to Text** - 99%+ accuracy with Whisper, speaker diarization
4. **Voice Conversion** - Transform voices while preserving content
5. **Real-Time Chat** - Full-duplex conversation with PersonaPlex
6. **Speech Translation** - Translate speech preserving voice
7. **Audio Enhancement** - AI-powered noise removal
8. **Custom Training** - Train your own voice models

## AI Models Used

### Text-to-Speech
- **Fish Speech v1.5** - Best quality, 13 languages, zero-shot cloning
- **Orpheus TTS 3B** - Emotion control, 100ms streaming
- **OpenVoice v2** - Fast voice conversion
- **XTTS v2** - 17 languages, fine-tunable

### Speech-to-Text
- **Whisper Large v3** - 100+ languages, 99%+ accuracy
- **Canary Qwen 2.5B** - Lowest WER

### Conversational
- **PersonaPlex 7B** - NVIDIA's full-duplex model (<200ms latency)

## Credit System

| Feature | Credits |
|---------|---------|
| Voice Cloning | 1 per clone |
| Text to Speech | 1 per 1000 chars |
| Speech to Text | 1 per minute |
| Voice Conversion | 2 per minute |
| Real-Time Chat | 1 per minute |
| Speech Translation | 3 per minute |
| Audio Enhancement | 1 per minute |
| Custom Training | 30-100 per job |

## API Integration

The frontend communicates with `api.imageeditor.ai` for GPU processing:

```python
import requests

response = requests.post(
    'https://api.imageeditor.ai/v1/voice-clone/',
    headers={'Authorization': f'Bearer {API_KEY}'},
    files={'file': audio_file},
    data={'model': 'fish-speech-v1.5'}
)
```

## Deployment

**Server**: DigitalOcean Droplet (167.172.17.40, s-2vcpu-4gb, nyc3)

### Initial Deployment
```bash
cd ansible && ansible-playbook -i servers djangodeployubuntu20.yml
```

### Manual Deployment Steps
```bash
# SSH to server
ssh root@167.172.17.40

# Update code
cd /home/www/speechtospeechai && git pull origin main

# Install requirements if changed
source venv/bin/activate && pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart
supervisorctl restart speechtospeechai
```

### Quick Deploy (via ansible from local)
```bash
cd ansible && ansible -i servers all -m shell -a "cd /home/www/speechtospeechai && git pull origin main && source venv/bin/activate && pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput && supervisorctl restart speechtospeechai" --become
```

### SSL Setup
```bash
ssh root@167.172.17.40
certbot --nginx -d speechtospeechai.com -d www.speechtospeechai.com
```

### Logs
```bash
# Application logs
tail -f /var/log/speechtospeechai/speechtospeechai.err.log
tail -f /var/log/speechtospeechai/speechtospeechai.out.log

# Django logs
cat /var/log/speechtospeechai/speechtospeechai.log

# Nginx logs
tail -f /var/log/nginx/error.log
```

### Database Access
```bash
ssh root@167.172.17.40
sudo -u postgres psql speechtospeechai
```

## Resources

- [PersonaPlex](https://research.nvidia.com/labs/adlr/personaplex/)
- [Fish Speech](https://github.com/fishaudio/fish-speech)
- [Orpheus TTS](https://github.com/canopyai/Orpheus-TTS)
- [OpenVoice](https://github.com/myshell-ai/OpenVoice)
