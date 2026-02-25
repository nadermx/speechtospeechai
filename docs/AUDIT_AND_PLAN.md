# SpeechToSpeechAI.com -- Audit and Expansion Plan

## Project Summary

SpeechToSpeechAI.com is a comprehensive speech AI platform featuring 9 TTS engines, voice cloning, real-time conversation, speech translation, audio enhancement, voice conversion, and stem separation. The frontend is a Django application on its own server (167.172.17.40) that delegates all GPU processing to the shared GPU server (38.248.6.142) via api.speechtospeechai.com. The JavaScript client (`speech-api.js`) handles all API communication with polling-based result retrieval.

**Stack**: Django + PostgreSQL + Redis + Gunicorn/Nginx/Supervisor
**Web Server**: 167.172.17.40 (DigitalOcean) | **GPU Backend**: 38.248.6.142 (4x Tesla P40)
**TTS Engines**: Piper, XTTS-v2, Bark, StyleTTS2, F5-TTS, OpenVoice, Tortoise, VITS, Parler
**Additional GPU Models**: Kokoro, Chatterbox-TTS, MeloTTS, Faster-Whisper, FunASR, Demucs, GPT-SoVITS, CosyVoice2, IndexTTS2, SparkTTS

---

## Current Feature Inventory

### Text-to-Speech (9+ Engines)
- Piper (fast, lightweight, VRAM <2GB)
- XTTS-v2 via Coqui TTS (multi-language, voice cloning capable)
- Bark (expressive, supports sound effects)
- StyleTTS2 (high quality, style transfer)
- F5-TTS (flow-matching, fast inference)
- OpenVoice (voice cloning + tone control)
- Tortoise (highest quality, slow)
- VITS (fast, multilingual)
- Parler (descriptive voice control)
- Plus: Kokoro, Chatterbox-TTS, MeloTTS on GPU

### Voice Cloning
- Upload audio sample, synthesize new speech in cloned voice
- 1 credit per clone operation
- Supports multiple languages with cloned voice

### Speech-to-Text
- Faster-Whisper for transcription
- FunASR as alternative backend
- 1 credit per minute of audio

### Voice Conversion
- Convert speaker identity while preserving content
- 2 credits per minute of audio

### Speech Translation
- Transcribe + translate + synthesize in target language
- End-to-end speech-to-speech translation
- 3 credits per minute (highest credit cost)

### Audio Enhancement
- Noise reduction (noisereduce library)
- Audio quality improvement
- 1 credit per minute

### Stem Separation
- Demucs-based source separation
- Isolate vocals, drums, bass, other instruments
- Useful for music production and karaoke

### Real-Time Conversation
- Dedicated page: /real-time-chat.html
- Conversational AI with speech input/output

### Platform
- Credits-based billing (Stripe, PayPal, Square, Coinbase)
- Custom email-based user auth (accounts.CustomUser)
- Database-driven i18n (translations app)
- Contact form with captcha
- API documentation page

---

## Bugs and Vulnerabilities

### Critical

1. **No apparent rate limiting documented**: Unlike TranslateAPI's dual-throttle system, there is no documented rate limiting for the speech API endpoints. Free users could potentially submit unlimited requests to the GPU server, consuming expensive VRAM and compute time. The GPU server's credit deduction callback provides some protection, but users with credits could drain GPU resources rapidly. Fix: implement per-user request throttling (requests/hour) matching the pattern from TranslateAPI.

2. **No sitemap**: The site has no XML sitemap for search engine indexing. With multiple tool pages (TTS, voice cloning, speech translation, etc.), this is a significant SEO gap. Fix: create a basic static sitemap for all tool pages.

3. **ansible_user is root**: The server uses root as the ansible_user, which is a security risk. The `disableroot.yml` playbook exists but was never run. Fix: create a dedicated deploy user, run disableroot.yml, and update the inventory.

4. **No gitpull.yml**: Deployment requires manual SSH commands or ad-hoc Ansible. This makes deployments error-prone and inconsistent. Fix: create a standard gitpull.yml playbook.

### Medium

5. **Voice cloning cost may be too low**: At 1 credit per clone, voice cloning is significantly underpriced relative to its GPU cost. A single clone operation loads a model, processes audio, and generates speech -- consuming 4-8GB VRAM for several seconds. Consider 2-3 credits per clone.

6. **No view tracking or smart retention**: Unlike 9 other projects that have view-based content retention, this project has no view_count, no download_count, no BOT_SIGNATURES. Generated audio files accumulate without cleanup intelligence. Fix: implement smart_expire pattern if audio results are stored persistently.

7. **Credit costs not enforced on frontend**: The credit system is documented in CLAUDE.md but the enforcement relies on the GPU server callback. If the callback mechanism fails, users could generate speech without credit deduction.

8. **No speech output caching**: Identical TTS requests (same text, same voice, same settings) recompute from scratch every time. For common phrases, this wastes GPU resources. Consider caching results by input hash.

### Low

9. **JavaScript client lacks error recovery**: `speech-api.js` polls for results but behavior on network errors or timeout is not documented. Long-running operations (Tortoise TTS can take minutes) may timeout on the client side.

10. **Custom training page exists but unclear status**: Template `custom-training.html` exists, suggesting a custom voice training feature. Unclear if this is live, planned, or abandoned.

11. **No usage analytics**: No tracking of which TTS engines are most popular, average generation times, or failure rates. Missing data for optimization decisions.

---

## Test Suite Plan

### Authentication & User Management
- `test_user_registration` -- email signup, verification code flow
- `test_user_login` -- email/password authentication, session creation
- `test_user_logout` -- session destruction, redirect
- `test_password_reset` -- restore_password_token email flow
- `test_email_verification` -- confirmation_token validation
- `test_user_credits_display` -- account page shows correct credit balance
- `test_user_plan_status` -- plan_subscribed and is_plan_active reflected in UI

### Payment Processing
- `test_stripe_checkout` -- charge creation, webhook handling, credit allocation
- `test_paypal_subscription` -- plan creation, IPN validation, recurring billing
- `test_square_payment` -- nonce-based payment processing
- `test_coinbase_payment` -- crypto payment webhook handling
- `test_subscription_rebilling` -- rebill command processes renewals correctly
- `test_plan_expiry` -- expire_pro_users deactivates lapsed subscriptions
- `test_credit_allocation_per_plan` -- each plan tier receives correct credits

### TTS Generation
- `test_tts_piper` -- Piper engine: fast, returns audio file
- `test_tts_xtts` -- XTTS-v2: multi-language, higher quality
- `test_tts_bark` -- Bark: expressive output with sound effects
- `test_tts_styletts2` -- StyleTTS2: style transfer capability
- `test_tts_f5` -- F5-TTS: flow-matching inference
- `test_tts_openvoice` -- OpenVoice: tone control
- `test_tts_tortoise` -- Tortoise: highest quality, long generation time
- `test_tts_vits` -- VITS: fast multilingual
- `test_tts_parler` -- Parler: descriptive voice control
- `test_tts_credit_deduction` -- 1 credit per 1000 chars deducted
- `test_tts_empty_text_rejected` -- empty or whitespace-only text returns error
- `test_tts_language_support` -- unsupported languages return clear error
- `test_tts_max_text_length` -- text exceeding limit returns error
- `test_tts_polling_flow` -- submit job, poll UUID, receive audio

### Voice Cloning
- `test_voice_clone_upload` -- audio file upload + text → cloned speech
- `test_voice_clone_credit_cost` -- 1 credit deducted per clone
- `test_voice_clone_invalid_audio` -- non-audio file rejected
- `test_voice_clone_short_sample` -- too-short audio sample returns error
- `test_voice_clone_language_support` -- cloned voice in different languages
- `test_voice_clone_file_size_limit` -- oversized files rejected

### Speech Translation
- `test_speech_translate_flow` -- audio in → transcription → translation → speech out
- `test_speech_translate_credit_cost` -- 3 credits per minute
- `test_speech_translate_language_pairs` -- supported pair validation
- `test_speech_translate_long_audio` -- handling of multi-minute audio
- `test_speech_translate_unsupported_language` -- clear error message

### Audio Enhancement
- `test_audio_enhance_noise_reduction` -- noisy audio → cleaned audio
- `test_audio_enhance_credit_cost` -- 1 credit per minute
- `test_audio_enhance_file_formats` -- mp3, wav, ogg, m4a support
- `test_audio_enhance_large_file` -- file size limit enforcement

### Voice Conversion
- `test_voice_convert_flow` -- source audio → target voice identity
- `test_voice_convert_credit_cost` -- 2 credits per minute
- `test_voice_convert_quality` -- output audio quality preserved

### Stem Separation
- `test_stem_separation_4stems` -- vocals, drums, bass, other isolated
- `test_stem_separation_2stems` -- vocals vs accompaniment
- `test_stem_separation_file_formats` -- mp3, wav, flac support
- `test_stem_separation_long_track` -- multi-minute audio processing

### Speech-to-Text
- `test_stt_transcription` -- audio → text transcription
- `test_stt_credit_cost` -- 1 credit per minute
- `test_stt_language_detection` -- auto-detect spoken language
- `test_stt_timestamps` -- word/segment level timestamps
- `test_stt_file_formats` -- mp3, wav, m4a, ogg, webm support

### JavaScript API Client
- `test_speech_api_tts_call` -- SpeechAPI.textToSpeech() sends correct payload
- `test_speech_api_clone_call` -- SpeechAPI.voiceClone() handles file upload
- `test_speech_api_polling` -- SpeechAPI.pollResults() retries until complete
- `test_speech_api_error_handling` -- graceful failure on network error
- `test_speech_api_timeout` -- long-running operations handled

---

## Expansion Roadmap

### Phase 1: Streaming & Real-Time (Q2 2026)

**Real-Time Voice Changer for Streaming/Gaming**
- WebSocket-based low-latency voice transformation
- Preset voice effects: deep, robotic, chipmunk, echo, whisper
- Custom voice profiles from cloned voices
- OBS plugin integration (Virtual Audio Cable)
- Discord/Twitch bot for live stream voice changing
- Latency target: <200ms for real-time conversation
- Revenue: gaming tier ($9.99/month), streamer tier ($19.99/month)

**Podcast Enhancement Suite**
- Multi-speaker diarization (identify who speaks when)
- Per-speaker noise reduction and leveling
- Automatic silence trimming and pacing adjustment
- Intro/outro music overlay with ducking
- Transcript generation with speaker labels
- Export to podcast platforms (RSS, Spotify, Apple)
- Revenue: podcaster tier ($14.99/month)

### Phase 2: Media Production (Q3 2026)

**Dubbing Platform**
- Upload video → extract audio → transcribe → translate → TTS in target language
- Lip-sync adjustment (adjust speech timing to match mouth movements)
- Multi-character dubbing (different voices per speaker)
- Subtitle generation alongside dub
- Support for 50+ target languages
- Revenue: per-minute pricing ($0.50-2.00/min depending on quality tier)

**Karaoke Generator**
- Upload song → Demucs stem separation → remove vocals
- Generate synchronized lyrics display
- Pitch-shifted backing tracks for different vocal ranges
- Export as video with lyrics overlay
- Revenue: per-song pricing ($0.99 free tier, unlimited for pro)

**Music Production Tools**
- Stem isolation for remixing (drums, bass, vocals, other)
- Vocal removal for sampling
- Key detection and BPM analysis
- Audio mastering (EQ, compression, limiting)
- Loop detection and extraction
- Revenue: producer tier ($24.99/month)

### Phase 3: Enterprise & Accessibility (Q4 2026)

**Enterprise Call Center Voices**
- Custom branded TTS voices trained on company spokesperson
- IVR system integration (Twilio, Vonage, Genesys)
- Multi-language customer service voices
- Emotion-appropriate responses (calm for complaints, enthusiastic for upgrades)
- Call recording → transcript → summary pipeline
- Revenue: enterprise tier ($500-5K/month per voice)

**Call Translation Service**
- Real-time phone call translation between two languages
- WebRTC-based browser phone integration
- Twilio integration for phone number provisioning
- Conference call mode (3+ participants, multiple languages)
- Revenue: per-minute pricing ($0.10-0.25/min)

**Accessibility for Speech Impaired**
- Personal voice banking (record voice before surgery/deterioration)
- AAC (Augmentative and Alternative Communication) integration
- Eye-tracking input for TTS output
- Emotion and emphasis control for natural communication
- Medical partnership program (subsidized pricing)
- Revenue: subsidized tier ($4.99/month), insurance reimbursement pathway

### Phase 4: Social & Consumer (2027)

**Voice Anonymization**
- Privacy-preserving voice transformation
- Consistent anonymized voice per session (recognizable but unidentifiable)
- Pitch, formant, and timbre manipulation
- Compliance with GDPR/CCPA voice data regulations
- Use cases: whistleblowers, support groups, anonymous reviews
- Revenue: privacy tier ($7.99/month)

**Gaming Voice Effects**
- Character voice presets (orc, elf, dragon, robot, alien)
- Dynamic voice modulation based on game events
- Unity/Unreal Engine SDK for game developers
- Voice chat integration (Steam, Epic, Xbox)
- Revenue: gaming SDK ($99/month for studios), consumer ($4.99/month)

**Language Learning Pronunciation**
- Record speech → compare to native pronunciation
- Phoneme-level accuracy scoring
- Accent identification and reduction coaching
- Shadowing exercises (listen + repeat + compare)
- Progress tracking with pronunciation improvement graphs
- Revenue: learner tier ($9.99/month)

**Social Voice Filters**
- Instagram/TikTok style voice effects for short-form video
- Voice beautification (smooth, warm, broadcast quality)
- Celebrity-style voice impressions (non-infringing stylistic transforms)
- Audio meme generator
- Revenue: social tier ($2.99/month), in-app purchases

---

## Revenue Impact Estimates

| Feature | Tier | Est. Monthly Revenue | Timeline |
|---------|------|---------------------|----------|
| Real-Time Voice Changer | Gaming/Streamer | $3K-10K | Q2 2026 |
| Podcast Enhancement | Podcaster | $2K-6K | Q2 2026 |
| Dubbing Platform | Per-minute | $5K-15K | Q3 2026 |
| Karaoke Generator | Per-song/Pro | $1K-3K | Q3 2026 |
| Music Production Tools | Producer | $3K-8K | Q3 2026 |
| Enterprise Call Center | Enterprise | $10K-50K | Q4 2026 |
| Call Translation | Per-minute | $3K-10K | Q4 2026 |
| Accessibility | Subsidized | $1K-3K | Q4 2026 |
| Voice Anonymization | Privacy | $1K-3K | 2027 |
| Gaming Voice Effects | SDK/Consumer | $5K-15K | 2027 |
| Language Learning | Learner | $3K-8K | 2027 |
| Social Voice Filters | Social | $2K-5K | 2027 |

---

## Priority Actions

1. **Implement rate limiting** -- add per-user request throttling before GPU submission (highest risk)
2. **Create gitpull.yml** -- standardize deployment (currently manual SSH)
3. **Run disableroot.yml** -- stop using root as ansible_user (security risk)
4. **Add XML sitemap** -- static sitemap for all tool pages (SEO gap)
5. **Review voice cloning pricing** -- 1 credit may be too low relative to GPU cost
6. **Implement speech output caching** -- cache by input hash to reduce redundant GPU work
7. **Add usage analytics** -- track engine popularity, generation times, failure rates
8. **Build real-time voice changer** as first expansion (streaming/gaming market is growing fast, high engagement)
