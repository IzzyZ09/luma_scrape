const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({
    storageState: 'auth.json' // contains your logged-in cookies
  });

  const page = await context.newPage();
  const urls = fs.readFileSync('linkedin_urls.txt', 'utf-8').split('\n');

  for (let url of urls) {
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(3000); // Let the profile load

      const headline = await page.locator('.text-body-medium').first().innerText();
      const about = await page.locator('.pv-about-section').innerText(); // fallback

      console.log(`\nURL: ${url}\nHeadline: ${headline}\nAbout: ${about}\n`);
    } catch (err) {
      console.error(`Error at ${url}:`, err);
    }
  }

  await browser.close();
})();
