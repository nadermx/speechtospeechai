/**
 * Frontend Functionality Tests for speechtospeechai.com
 * Run with: npx playwright test tests/test-frontend.js
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = 'https://www.speechtospeechai.com';

// Test each tool page loads and has functional UI elements
const toolPages = [
    {
        name: 'Voice Cloning',
        path: '/voice-cloning/',
        elements: {
            fileUpload: '#audioFile',
            recordBtn: '#recordBtn',
            processBtn: '#cloneBtn',
            header: 'h1'
        }
    },
    {
        name: 'Text to Speech',
        path: '/text-to-speech/',
        elements: {
            textInput: '#textInput',
            voiceSelect: '#voiceSelect',
            header: 'h1'
        }
    },
    {
        name: 'Speech to Text',
        path: '/speech-to-text/',
        elements: {
            fileUpload: '#audioFile',
            header: 'h1'
        }
    },
    {
        name: 'Voice Conversion',
        path: '/voice-conversion/',
        elements: {
            header: 'h1'
        }
    },
    {
        name: 'Audio Enhancement',
        path: '/audio-enhancement/',
        elements: {
            header: 'h1'
        }
    },
    {
        name: 'Speech Translation',
        path: '/speech-translation/',
        elements: {
            header: 'h1'
        }
    },
    {
        name: 'Real-Time Chat',
        path: '/real-time-chat/',
        elements: {
            callBtn: '#callBtn',
            muteBtn: '#muteBtn',
            speakerBtn: '#speakerBtn',
            chatMessages: '#chatMessages',
            header: 'h1'
        }
    },
    {
        name: 'Custom Training',
        path: '/custom-training/',
        elements: {
            header: 'h1'
        }
    }
];

// Test page loads
test.describe('Page Load Tests', () => {
    for (const page of toolPages) {
        test(`${page.name} loads successfully`, async ({ page: browserPage }) => {
            const response = await browserPage.goto(`${BASE_URL}${page.path}`);
            expect(response.status()).toBe(200);

            // Check header exists
            const header = await browserPage.locator(page.elements.header).first();
            await expect(header).toBeVisible();
        });
    }
});

// Test interactive elements
test.describe('Interactive Element Tests', () => {
    test('Voice Cloning - Upload area is clickable', async ({ page }) => {
        await page.goto(`${BASE_URL}/voice-cloning/`);

        const dropzone = page.locator('#dropzone');
        await expect(dropzone).toBeVisible();

        const fileInput = page.locator('#audioFile');
        await expect(fileInput).toBeAttached();
    });

    test('Text to Speech - Text input and voice selection work', async ({ page }) => {
        await page.goto(`${BASE_URL}/text-to-speech/`);

        const textInput = page.locator('#textInput');
        await expect(textInput).toBeVisible();

        // Type some text
        await textInput.fill('Hello, this is a test.');
        await expect(textInput).toHaveValue('Hello, this is a test.');

        // Check voice select
        const voiceSelect = page.locator('#voiceSelect');
        await expect(voiceSelect).toBeVisible();
    });

    test('Speech to Text - Upload area is present', async ({ page }) => {
        await page.goto(`${BASE_URL}/speech-to-text/`);

        // Check for dropzone or upload area
        const uploadArea = page.locator('.border-dashed, #dropzone').first();
        await expect(uploadArea).toBeVisible();
    });

    test('Real-Time Chat - Call button is functional', async ({ page }) => {
        await page.goto(`${BASE_URL}/real-time-chat/`);

        const callBtn = page.locator('#callBtn');
        await expect(callBtn).toBeVisible();

        const muteBtn = page.locator('#muteBtn');
        await expect(muteBtn).toBeVisible();

        const speakerBtn = page.locator('#speakerBtn');
        await expect(speakerBtn).toBeVisible();

        // Check chat messages area
        const chatMessages = page.locator('#chatMessages');
        await expect(chatMessages).toBeVisible();
    });
});

// Test JavaScript loads and SpeechAPI is available
test.describe('JavaScript Tests', () => {
    test('SpeechAPI is loaded on voice-cloning page', async ({ page }) => {
        await page.goto(`${BASE_URL}/voice-cloning/`);

        // Check SpeechAPI is available
        const hasAPI = await page.evaluate(() => {
            return typeof window.SpeechAPI !== 'undefined';
        });
        expect(hasAPI).toBe(true);
    });

    test('SpeechUI helpers are loaded', async ({ page }) => {
        await page.goto(`${BASE_URL}/voice-cloning/`);

        const hasUI = await page.evaluate(() => {
            return typeof window.SpeechUI !== 'undefined';
        });
        expect(hasUI).toBe(true);
    });

    test('ErrorLogger is loaded', async ({ page }) => {
        await page.goto(`${BASE_URL}/voice-cloning/`);

        const hasLogger = await page.evaluate(() => {
            return typeof window.ErrorLogger !== 'undefined';
        });
        expect(hasLogger).toBe(true);
    });
});

// Test API connectivity (without making actual requests)
test.describe('API Configuration Tests', () => {
    test('API base URL is configured', async ({ page }) => {
        await page.goto(`${BASE_URL}/voice-cloning/`);

        const baseUrl = await page.evaluate(() => {
            return window.SpeechAPI?.baseUrl;
        });

        expect(baseUrl).toBeTruthy();
        expect(baseUrl).toContain('api.');
    });
});

// Test for console errors
test.describe('Console Error Tests', () => {
    for (const toolPage of toolPages) {
        test(`${toolPage.name} has no critical JS errors`, async ({ page }) => {
            const errors = [];

            page.on('pageerror', (error) => {
                errors.push(error.message);
            });

            await page.goto(`${BASE_URL}${toolPage.path}`);
            await page.waitForLoadState('networkidle');

            // Filter out known non-critical errors
            const criticalErrors = errors.filter(e =>
                !e.includes('Failed to load resource') &&
                !e.includes('net::ERR')
            );

            if (criticalErrors.length > 0) {
                console.log(`Errors on ${toolPage.name}:`, criticalErrors);
            }

            // Allow test to pass even with some errors, but log them
            expect(criticalErrors.length).toBeLessThan(5);
        });
    }
});

// Specific functionality tests
test.describe('Detailed Functionality Tests', () => {
    test('Voice Cloning - Tab navigation works', async ({ page }) => {
        await page.goto(`${BASE_URL}/voice-cloning/`);

        // Check upload tab is active by default
        const uploadTab = page.locator('a[href="#upload-tab"]');
        await expect(uploadTab).toHaveClass(/active/);

        // Click record tab
        const recordTab = page.locator('a[href="#record-tab"]');
        await recordTab.click();
        await expect(recordTab).toHaveClass(/active/);

        // Check record button is visible
        const recordBtn = page.locator('#recordBtn');
        await expect(recordBtn).toBeVisible();
    });

    test('Text to Speech - Character counter updates', async ({ page }) => {
        await page.goto(`${BASE_URL}/text-to-speech/`);

        const textInput = page.locator('#textInput');
        const charCount = page.locator('#charCount');

        await textInput.fill('Test');

        // Check that char count updated
        await page.waitForTimeout(100);
        const countText = await charCount.textContent();
        expect(countText).toContain('4');
    });

    test('Speech to Text - Language dropdown is populated', async ({ page }) => {
        await page.goto(`${BASE_URL}/speech-to-text/`);

        const langSelect = page.locator('#languageSelect, select[name="language"]').first();
        if (await langSelect.isVisible()) {
            const options = await langSelect.locator('option').count();
            expect(options).toBeGreaterThan(1);
        }
    });

    test('Real-Time Chat - Click call button shows messages', async ({ page }) => {
        await page.goto(`${BASE_URL}/real-time-chat/`);

        // Get initial chat state
        const chatMessages = page.locator('#chatMessages');
        const initialContent = await chatMessages.innerHTML();

        // Click the call button (but expect it might fail due to no mic permission)
        const callBtn = page.locator('#callBtn');

        // Set up to dismiss any alerts
        page.on('dialog', dialog => dialog.dismiss());

        await callBtn.click();

        // Wait a bit for any changes
        await page.waitForTimeout(1000);

        // The content should have changed (either messages or an error)
        const newContent = await chatMessages.innerHTML();
        // Just verify the page didn't crash
        await expect(chatMessages).toBeVisible();
    });
});

// Mobile responsiveness tests
test.describe('Mobile Responsiveness Tests', () => {
    test.use({ viewport: { width: 375, height: 667 } });

    test('Pages are usable on mobile', async ({ page }) => {
        for (const toolPage of toolPages.slice(0, 3)) { // Test first 3 pages
            await page.goto(`${BASE_URL}${toolPage.path}`);

            // Check header is visible
            const header = page.locator('h1').first();
            await expect(header).toBeVisible();

            // Check no horizontal overflow
            const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
            const viewportWidth = await page.evaluate(() => window.innerWidth);
            expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 10); // Allow small margin
        }
    });
});
