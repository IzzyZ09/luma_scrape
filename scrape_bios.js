const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: false }); // set to true to run in bg
  const context = await browser.newContext({ storageState: 'auth.json' });

  const allLines = fs.readFileSync('linkedin_urls.txt', 'utf-8')
    .split('\n')
    .map(line => line.trim());

  const urls = [];
  const skipped = [];

  // separate valid profile URLs and skipped URLs
  for (const line of allLines) {
    if (line && line.includes('/in/')) {
      urls.push(line);
    } else if (line) {
      skipped.push(line);
    }
  }

  const output = [['URL', 'Headline', 'About']];
  const failed = [];

  const scrapeProfile = async (url) => {
    const page = await context.newPage();
    try {
      console.log(`Visiting: ${url}`);
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });

      const headline = await page.locator('.text-body-medium').first().innerText().catch(() => '');
      const about = await page.locator('section.pv-about-section').first().innerText().catch(() => '');

      output.push([url, headline, about]);
      console.log(`Scraped: ${headline}`);
    } catch (err) {
      console.log(`Failed: ${url} — ${err.message}`);
      output.push([url, '', '']);
      failed.push(url);
    } finally {
      await page.close();
    }
  };

  const batchSize = 5; // how many profiles to scrape in each batch
  for (let i = 0; i < urls.length; i += batchSize) {
    const batch = urls.slice(i, i + batchSize);
    await Promise.all(batch.map(scrapeProfile));
  }

  // save main CSV
  const csv = output.map(row =>
    row.map(field => `"${(field || '').replace(/"/g, '""')}"`).join(',')
  ).join('\n');
  fs.writeFileSync('linkedin_bios.csv', '\uFEFF' + csv);

  // save failed URLs
  if (failed.length > 0) {
    fs.writeFileSync('failed_urls.txt', failed.join('\n'));
    console.log(`${failed.length} URLs failed, saved to failed_urls.txt`);
  }

  // save skipped URLs
  if (skipped.length > 0) {
    fs.writeFileSync('skipped_urls.txt', skipped.join('\n'));
    console.log(`${skipped.length} URLs skipped, saved to skipped_urls.txt`);
  }

  console.log('All bios saved to linkedin_bios.csv');
  await browser.close();
})();
