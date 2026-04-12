const { chromium } = require('playwright');
const path = require('path');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    // Capture console errors
    const errors = [];
    page.on('console', msg => {
        if (msg.type() === 'error') errors.push(msg.text());
    });
    page.on('pageerror', err => errors.push(err.message));

    await page.goto('https://hanyunfan.github.io/co-parenting-portal/', { waitUntil: 'networkidle' });

    // Wait for calendar to render
    await page.waitForTimeout(2000);

    // Check if calendar has day numbers
    const dayNums = await page.locator('.day-num').count();
    const dayLabels = await page.locator('.day-label').count();
    const calDays = await page.locator('.cal-day').count();

    console.log(`cal-day count: ${calDays}`);
    console.log(`day-num count: ${dayNums}`);
    console.log(`day-label count: ${dayLabels}`);

    if (errors.length > 0) {
        console.log('ERRORS:', errors);
    } else {
        console.log('No console errors');
    }

    // Get first few day-num texts
    const firstDays = await page.locator('.day-num').allTextContents();
    console.log('First 10 day nums:', firstDays.slice(0, 10));

    // Check which tab is active
    const activeTab = await page.locator('.nav-tab.active').textContent();
    console.log('Active tab:', activeTab);

    // Check which calendar container is visible
    const spoVisible = await page.locator('#spoContainer').isVisible();
    const espoVisible = await page.locator('#espoContainer').isVisible();
    console.log('spoContainer visible:', spoVisible);
    console.log('espoContainer visible:', espoVisible);

    await browser.close();
})();
