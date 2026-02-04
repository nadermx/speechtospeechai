const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
    testDir: './tests',
    timeout: 30000,
    use: {
        baseURL: 'https://www.speechtospeechai.com',
        headless: true,
        screenshot: 'only-on-failure',
    },
    reporter: 'list',
});
