/**
 * Frontend Functionality Tests for speechtospeechai.com
 * Run with: npx playwright test tests/frontend.spec.js
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = 'https://www.speechtospeechai.com';

// All tool pages configuration
const toolPages = [
    {
        name: 'Voice Cloning',
        path: '/voice-cloning/',
        hasFileUpload: true,
        hasRecording: true,
        primaryButton: '#cloneBtn',
        elements: ['#dropzone', '#textToSpeak']
    },
    {
        name: 'Text to Speech',
        path: '/text-to-speech/',
        hasFileUpload: false,
        hasRecording: false,
        primaryButton: '#generateBtn',
        elements: ['#textInput', '#voiceSelect', '#modelSelect']
    },
    {
        name: 'Speech to Text',
        path: '/speech-to-text/',
        hasFileUpload: true,
        hasRecording: true,
        primaryButton: '#transcribeBtn',
        elements: ['#dropzone', '#languageSelect']
    },
    {
        name: 'Voice Conversion',
        path: '/voice-conversion/',
        hasFileUpload: true,
        hasRecording: false,
        primaryButton: '#convertBtn',
        elements: ['#sourceDropzone', '#targetDropzone']
    },
    {
        name: 'Audio Enhancement',
        path: '/audio-enhancement/',
        hasFileUpload: true,
        hasRecording: false,
        primaryButton: '#enhanceBtn',
        elements: ['#dropzone']
    },
    {
        name: 'Speech Translation',
        path: '/speech-translation/',
        hasFileUpload: true,
        hasRecording: false,
        primaryButton: '#translateBtn',
        elements: ['#dropzone', '#targetLang']
    },
    {
        name: 'Real-Time Chat',
        path: '/real-time-chat/',
        hasFileUpload: false,
        hasRecording: false,
        primaryButton: '#callBtn',
        elements: ['#chatMessages', '#muteBtn', '#speakerBtn']
    },
    {
        name: 'Custom Training',
        path: '/custom-training/',
        hasFileUpload: true,
        hasRecording: false,
        primaryButton: '.btn-primary',
        elements: ['#voiceName']
    }
];

// Static pages
const staticPages = [
    { path: '/', name: 'Home' },
    { path: '/pricing/', name: 'Pricing' },
    { path: '/api-docs/', name: 'API Docs' },
    { path: '/models/', name: 'Models' },
    { path: '/about/', name: 'About' },
    { path: '/contact/', name: 'Contact' },
    { path: '/login/', name: 'Login' },
    { path: '/signup/', name: 'Signup' },
    { path: '/privacy/', name: 'Privacy' },
    { path: '/terms/', name: 'Terms' }
];

// ==========================================
// PAGE LOAD TESTS
// ==========================================
test.describe('Page Load Tests', () => {
    for (const page of [...toolPages, ...staticPages]) {
        test(`${page.name} page loads (200 OK)`, async ({ page: browserPage }) => {
            const response = await browserPage.goto(`${BASE_URL}${page.path}`, {
                waitUntil: 'domcontentloaded'
            });
            expect(response.status()).toBe(200);

            // Check page has content
            const body = await browserPage.locator('body');
            await expect(body).toBeVisible();
        });
    }
});

// ==========================================
// NAVIGATION TESTS
// ==========================================
test.describe('Navigation Tests', () => {
    test('Navbar links work correctly', async ({ page }) => {
        await page.goto(BASE_URL);

        // Test Tools dropdown
        const toolsDropdown = page.locator('#toolsDropdown');
        await expect(toolsDropdown).toBeVisible();
        await toolsDropdown.click();

        // Check dropdown items are visible
        const voiceCloningLink = page.locator('a[href="/voice-cloning/"]').first();
        await expect(voiceCloningLink).toBeVisible();
    });

    test('Footer links are present', async ({ page }) => {
        await page.goto(BASE_URL);

        const footer = page.locator('footer');
        await expect(footer).toBeVisible();

        // Check for key footer links
        await expect(page.locator('footer a[href="/privacy/"]')).toBeVisible();
        await expect(page.locator('footer a[href="/terms/"]')).toBeVisible();
    });

    test('Logo navigates to home', async ({ page }) => {
        await page.goto(`${BASE_URL}/pricing/`);

        const logo = page.locator('.navbar-brand').first();
        await logo.click();

        await expect(page).toHaveURL(/\//);
    });
});

// ==========================================
// JAVASCRIPT LOADING TESTS
// ==========================================
test.describe('JavaScript Tests', () => {
    test('SpeechAPI is loaded globally', async ({ page }) => {
        await page.goto(`${BASE_URL}/voice-cloning/`);
        await page.waitForLoadState('networkidle');

        const hasSpeechAPI = await page.evaluate(() => {
            return typeof window.SpeechAPI === 'object' &&
                   typeof window.SpeechAPI.textToSpeech === 'function';
        });
        expect(hasSpeechAPI).toBe(true);
    });

    test('SpeechUI helpers are loaded', async ({ page }) => {
        await page.goto(`${BASE_URL}/text-to-speech/`);
        await page.waitForLoadState('networkidle');

        const hasSpeechUI = await page.evaluate(() => {
            return typeof window.SpeechUI === 'object' &&
                   typeof window.SpeechUI.showLoading === 'function';
        });
        expect(hasSpeechUI).toBe(true);
    });

    test('ErrorLogger is loaded', async ({ page }) => {
        await page.goto(`${BASE_URL}/voice-cloning/`);
        await page.waitForLoadState('networkidle');

        const hasErrorLogger = await page.evaluate(() => {
            return typeof window.ErrorLogger === 'object' &&
                   typeof window.ErrorLogger.log === 'function';
        });
        expect(hasErrorLogger).toBe(true);
    });

    test('FileUploader class is available', async ({ page }) => {
        await page.goto(`${BASE_URL}/voice-cloning/`);
        await page.waitForLoadState('networkidle');

        const hasFileUploader = await page.evaluate(() => {
            return typeof window.FileUploader === 'function';
        });
        expect(hasFileUploader).toBe(true);
    });

    test('AudioRecorder class is available', async ({ page }) => {
        await page.goto(`${BASE_URL}/voice-cloning/`);
        await page.waitForLoadState('networkidle');

        const hasAudioRecorder = await page.evaluate(() => {
            return typeof window.AudioRecorder === 'function';
        });
        expect(hasAudioRecorder).toBe(true);
    });

    test('API_SERVER is configured', async ({ page }) => {
        await page.goto(`${BASE_URL}/voice-cloning/`);
        await page.waitForLoadState('networkidle');

        const apiServer = await page.evaluate(() => window.API_SERVER);
        expect(apiServer).toBeTruthy();
        expect(apiServer).toContain('api.');
    });
});

// ==========================================
// CONSOLE ERROR TESTS
// ==========================================
test.describe('Console Error Tests', () => {
    for (const toolPage of toolPages) {
        test(`${toolPage.name} has no critical JS errors`, async ({ page }) => {
            const errors = [];

            page.on('pageerror', (error) => {
                // Filter out known non-critical errors
                const msg = error.message.toLowerCase();
                if (!msg.includes('failed to load resource') &&
                    !msg.includes('net::err') &&
                    !msg.includes('recaptcha')) {
                    errors.push(error.message);
                }
            });

            await page.goto(`${BASE_URL}${toolPage.path}`);
            await page.waitForLoadState('networkidle');

            if (errors.length > 0) {
                console.log(`JS errors on ${toolPage.name}:`, errors);
            }

            expect(errors.length).toBe(0);
        });
    }
});

// ==========================================
// TOOL UI ELEMENT TESTS
// ==========================================
test.describe('Tool UI Elements', () => {
    test('Voice Cloning - All elements present', async ({ page }) => {
        await page.goto(`${BASE_URL}/voice-cloning/`);

        // Check dropzone
        const dropzone = page.locator('#dropzone');
        await expect(dropzone).toBeVisible();

        // Check audio file input
        const audioFile = page.locator('#audioFile');
        await expect(audioFile).toBeAttached();

        // Check clone button
        const cloneBtn = page.locator('#cloneBtn');
        await expect(cloneBtn).toBeVisible();

        // Check tab navigation (nav-link elements for tabs)
        const tabs = page.locator('.nav-tabs .nav-link');
        expect(await tabs.count()).toBeGreaterThanOrEqual(2);
    });

    test('Text to Speech - All elements present', async ({ page }) => {
        await page.goto(`${BASE_URL}/text-to-speech/`);

        // Text input
        const textInput = page.locator('#textInput');
        await expect(textInput).toBeVisible();

        // Voice select
        const voiceSelect = page.locator('#voiceSelect');
        await expect(voiceSelect).toBeVisible();

        // Model select
        const modelSelect = page.locator('#modelSelect');
        await expect(modelSelect).toBeVisible();

        // Speed slider
        const speedRange = page.locator('#speedRange');
        await expect(speedRange).toBeVisible();

        // Generate button
        const generateBtn = page.locator('#generateBtn');
        await expect(generateBtn).toBeVisible();
    });

    test('Speech to Text - All elements present', async ({ page }) => {
        await page.goto(`${BASE_URL}/speech-to-text/`);

        // Check for dropzone
        const dropzone = page.locator('#dropzone, .border-dashed').first();
        await expect(dropzone).toBeVisible();

        // Language select
        const langSelect = page.locator('#languageSelect');
        if (await langSelect.count() > 0) {
            await expect(langSelect).toBeVisible();
        }

        // Model select
        const modelSelect = page.locator('#modelSelect');
        if (await modelSelect.count() > 0) {
            await expect(modelSelect).toBeVisible();
        }
    });

    test('Real-Time Chat - All elements present', async ({ page }) => {
        await page.goto(`${BASE_URL}/real-time-chat/`);

        // Call button
        const callBtn = page.locator('#callBtn');
        await expect(callBtn).toBeVisible();

        // Mute button
        const muteBtn = page.locator('#muteBtn');
        await expect(muteBtn).toBeVisible();

        // Speaker button
        const speakerBtn = page.locator('#speakerBtn');
        await expect(speakerBtn).toBeVisible();

        // Chat messages
        const chatMessages = page.locator('#chatMessages');
        await expect(chatMessages).toBeVisible();
    });
});

// ==========================================
// FORM INTERACTION TESTS
// ==========================================
test.describe('Form Interaction Tests', () => {
    test('Text to Speech - Text input and character count', async ({ page }) => {
        await page.goto(`${BASE_URL}/text-to-speech/`);

        const textInput = page.locator('#textInput');
        const charCount = page.locator('#charCount');

        // Type text and dispatch input event
        await textInput.fill('Hello, this is a test of the speech synthesis system.');
        await textInput.dispatchEvent('input');

        // Wait for character count update
        await page.waitForTimeout(200);

        // Check character count updated
        const countText = await charCount.textContent();
        expect(countText).toMatch(/\d+/);  // Contains a number
    });

    test('Text to Speech - Speed slider updates', async ({ page }) => {
        await page.goto(`${BASE_URL}/text-to-speech/`);

        const speedRange = page.locator('#speedRange');
        const speedValue = page.locator('#speedValue');

        // Change speed
        await speedRange.fill('1.5');
        await speedRange.dispatchEvent('input');

        const valueText = await speedValue.textContent();
        expect(valueText).toContain('1.5');
    });

    test('Text to Speech - Sample button fills text', async ({ page }) => {
        await page.goto(`${BASE_URL}/text-to-speech/`);

        const sampleBtn = page.locator('button[title="Sample text"]');
        const textInput = page.locator('#textInput');

        await sampleBtn.click();

        const value = await textInput.inputValue();
        expect(value.length).toBeGreaterThan(10);
    });

    test('Text to Speech - Clear button clears text', async ({ page }) => {
        await page.goto(`${BASE_URL}/text-to-speech/`);

        const textInput = page.locator('#textInput');
        const clearBtn = page.locator('button[title="Clear text"]');

        await textInput.fill('Test text');
        await clearBtn.click();

        const value = await textInput.inputValue();
        expect(value).toBe('');
    });

    test('Voice Cloning - Tab switching works', async ({ page }) => {
        await page.goto(`${BASE_URL}/voice-cloning/`);

        // Click record tab
        const recordTab = page.locator('a[href="#record-tab"], button[data-bs-target="#record-tab"]').first();
        if (await recordTab.count() > 0) {
            await recordTab.click();

            // Record button should now be visible
            const recordBtn = page.locator('#recordBtn');
            await expect(recordBtn).toBeVisible();
        }
    });
});

// ==========================================
// API ERROR HANDLING TESTS (Unauthenticated)
// ==========================================
test.describe('Unauthenticated API Handling', () => {
    test('Text to Speech - Shows login prompt on generate (no API key)', async ({ page }) => {
        await page.goto(`${BASE_URL}/text-to-speech/`);

        // Fill in text
        const textInput = page.locator('#textInput');
        await textInput.fill('Test text for synthesis');

        // Try to generate
        const generateBtn = page.locator('#generateBtn');
        await generateBtn.click();

        // Wait for error response
        await page.waitForTimeout(2000);

        // Should show error card with API key message
        const outputCard = page.locator('#outputCard');
        await expect(outputCard).toBeVisible();

        const content = await outputCard.textContent();
        expect(content.toLowerCase()).toMatch(/api key|log in|sign up/);
    });

    test('Voice Cloning - Clone button is present but disabled without file', async ({ page }) => {
        await page.goto(`${BASE_URL}/voice-cloning/`);

        // Clone button should be present
        const cloneBtn = page.locator('#cloneBtn');
        await expect(cloneBtn).toBeVisible();

        // Button should be disabled by default (no file uploaded)
        await expect(cloneBtn).toBeDisabled();

        // Page should still be on voice-cloning
        await expect(page).toHaveURL(/voice-cloning/);
    });

    test('Real-Time Chat - Call button shows appropriate message', async ({ page }) => {
        await page.goto(`${BASE_URL}/real-time-chat/`);

        const callBtn = page.locator('#callBtn');
        const chatMessages = page.locator('#chatMessages');

        // Dismiss permission dialogs
        page.on('dialog', dialog => dialog.dismiss());

        await callBtn.click();

        // Wait for response
        await page.waitForTimeout(2000);

        // Chat should have some content (error or welcome)
        const content = await chatMessages.innerHTML();
        expect(content.length).toBeGreaterThan(0);
    });
});

// ==========================================
// MOBILE RESPONSIVENESS TESTS
// ==========================================
test.describe('Mobile Responsiveness', () => {
    test.use({ viewport: { width: 375, height: 667 } });

    for (const toolPage of toolPages) {
        test(`${toolPage.name} is responsive on mobile`, async ({ page }) => {
            await page.goto(`${BASE_URL}${toolPage.path}`);

            // Header visible
            const header = page.locator('h1').first();
            await expect(header).toBeVisible();

            // No horizontal scroll
            const hasOverflow = await page.evaluate(() => {
                return document.documentElement.scrollWidth > document.documentElement.clientWidth;
            });
            expect(hasOverflow).toBe(false);

            // Mobile menu toggle visible
            const menuToggle = page.locator('.navbar-toggler');
            await expect(menuToggle).toBeVisible();
        });
    }
});

// ==========================================
// ACCESSIBILITY TESTS
// ==========================================
test.describe('Accessibility Tests', () => {
    test('Pages have proper heading structure', async ({ page }) => {
        for (const toolPage of toolPages.slice(0, 3)) {
            await page.goto(`${BASE_URL}${toolPage.path}`);

            // Has h1
            const h1 = page.locator('h1');
            expect(await h1.count()).toBeGreaterThan(0);
        }
    });

    test('Form inputs have labels', async ({ page }) => {
        await page.goto(`${BASE_URL}/text-to-speech/`);

        // Check voice select has label
        const voiceLabel = page.locator('label[for="voiceSelect"], label:has-text("Voice")');
        expect(await voiceLabel.count()).toBeGreaterThan(0);
    });

    test('Buttons are keyboard accessible', async ({ page }) => {
        await page.goto(`${BASE_URL}/text-to-speech/`);

        const generateBtn = page.locator('#generateBtn');

        // Focus the button
        await generateBtn.focus();

        // Check it's focusable
        const isFocused = await page.evaluate(() => {
            return document.activeElement.id === 'generateBtn';
        });
        expect(isFocused).toBe(true);
    });
});

// ==========================================
// LOGIN/SIGNUP PAGES
// ==========================================
test.describe('Auth Pages', () => {
    test('Login form is functional', async ({ page }) => {
        await page.goto(`${BASE_URL}/login/`);

        // Email input
        const emailInput = page.locator('input[type="email"], input[name="email"]');
        await expect(emailInput).toBeVisible();

        // Password input
        const passwordInput = page.locator('input[type="password"]');
        await expect(passwordInput).toBeVisible();

        // Submit button
        const submitBtn = page.locator('button[type="submit"]');
        await expect(submitBtn).toBeVisible();
    });

    test('Signup form is functional', async ({ page }) => {
        await page.goto(`${BASE_URL}/signup/`);

        // Email input
        const emailInput = page.locator('input[type="email"], input[name="email"]');
        await expect(emailInput).toBeVisible();

        // Password inputs
        const passwordInputs = page.locator('input[type="password"]');
        expect(await passwordInputs.count()).toBeGreaterThanOrEqual(1);

        // Submit button
        const submitBtn = page.locator('button[type="submit"]');
        await expect(submitBtn).toBeVisible();
    });
});

// ==========================================
// PRICING PAGE TESTS
// ==========================================
test.describe('Pricing Page', () => {
    test('Pricing plans are displayed', async ({ page }) => {
        await page.goto(`${BASE_URL}/pricing/`);

        // Check for plan cards
        const planCards = page.locator('.card, .pricing-card');
        expect(await planCards.count()).toBeGreaterThanOrEqual(1);

        // Check for pricing info
        const priceText = page.locator('text=/\\$\\d+/');
        expect(await priceText.count()).toBeGreaterThan(0);
    });

    test('Get Started buttons are present', async ({ page }) => {
        await page.goto(`${BASE_URL}/pricing/`);

        const ctaButtons = page.locator('a:has-text("Get Started"), a:has-text("Subscribe"), button:has-text("Get Started")');
        expect(await ctaButtons.count()).toBeGreaterThan(0);
    });
});

// ==========================================
// CONTACT PAGE TESTS
// ==========================================
test.describe('Contact Page', () => {
    test('Contact form is functional', async ({ page }) => {
        await page.goto(`${BASE_URL}/contact/`);

        // Email input
        const emailInput = page.locator('input[name="email"]');
        await expect(emailInput).toBeVisible();

        // Message textarea
        const messageInput = page.locator('textarea[name="message"]');
        await expect(messageInput).toBeVisible();

        // Submit button
        const submitBtn = page.locator('button.btn-primary');
        await expect(submitBtn).toBeVisible();
    });
});
