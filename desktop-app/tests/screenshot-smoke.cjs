const { chromium } = require('playwright');
const fs = require('node:fs/promises');
const path = require('node:path');

async function main() {
  const outputDir = path.join(__dirname, '..', 'test-results');
  await fs.mkdir(outputDir, { recursive: true });

  const browser = await chromium.launch({
    headless: true
  });

  try {
    const page = await browser.newPage({
      viewport: { width: 1440, height: 900 },
      deviceScaleFactor: 1,
      ignoreHTTPSErrors: false
    });

    await page.goto('https://example.com', {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });

    const screenshotPath = path.join(
      outputDir,
      'example-com.png'
    );

    await page.screenshot({
      path: screenshotPath,
      fullPage: true
    });

    console.log('TITLE:', await page.title());
    console.log('URL:', page.url());
    console.log('SCREENSHOT:', screenshotPath);
  } finally {
    await browser.close();
  }
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
