const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false }); // opens real browser window
  const context = await browser.newContext();
  const page = await context.newPage();

  await page.goto('https://www.linkedin.com/login');
  console.log('🧠 Log into LinkedIn — take your time!');

  await page.waitForTimeout(60000); // 60 sec to log in manually

  await context.storageState({ path: 'auth.json' }); // saves login
  console.log('✅ Login saved!');
  await browser.close();
})();
