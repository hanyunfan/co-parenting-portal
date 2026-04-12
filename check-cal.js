const { chromium } = require('C:/Users/frank/AppData/Roaming/npm/node_modules/@playwright/test');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    const errors = [];
    page.on('console', msg => {
        if (msg.type() === 'error') errors.push('[ERROR] ' + msg.text());
    });
    page.on('pageerror', err => errors.push('[PAGEERROR] ' + err.message));

    await page.goto('https://hanyunfan.github.io/co-parenting-portal/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);

    // Click Calendar tab
    await page.click('#tabCalendar');
    await page.waitForTimeout(2000);

    // Take screenshot
    await page.screenshot({ path: 'C:/Users/frank/.openclaw/workspace/projects/co-parenting-portal/calendar-tab.png', fullPage: true });

    // Count elements
    const calDays = await page.locator('#espoContainer .cal-day').count();
    const dayNums = await page.locator('#espoContainer .day-num').count();
    const dayLabels = await page.locator('#espoContainer .day-label').count();

    console.log('After clicking Calendar tab:');
    console.log('  cal-day count:', calDays);
    console.log('  day-num count:', dayNums);
    console.log('  day-label count:', dayLabels);

    // Get first 5 day-num texts
    const firstDays = await page.locator('#espoContainer .day-num').allTextContents();
    console.log('  First 10 day nums:', firstDays.slice(0, 10));

    if (errors.length > 0) {
        console.log('ERRORS:', errors.join('\n'));
    } else {
        console.log('  No console errors');
    }

    await browser.close();
})();
