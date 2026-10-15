const { chromium } = require('playwright');
const fs = require('node:fs/promises');
const path = require('node:path');
const os = require('node:os');
const { validateDomain } = require('./discovery');

function validateTargets(input) {
  if (!Array.isArray(input) || input.length < 1 || input.length > 20) {
    throw new Error('Select between 1 and 20 hostnames.');
  }

  return [...new Set(input.map(validateDomain))];
}

async function captureHosts(input, outputDir) {
  const hosts = validateTargets(input);

  const destination = outputDir || path.join(
    os.homedir(),
    'WebShutter',
    'captures',
    new Date().toISOString().replace(/[:.]/g, '-')
  );

  await fs.mkdir(destination, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const results = [];

  try {
    for (let i = 0; i < hosts.length; i++) {
      const host = hosts[i];
      const page = await browser.newPage({
        viewport: { width: 1440, height: 900 },
        ignoreHTTPSErrors: false
      });

      const filename = `${String(i + 1).padStart(3, '0')}-${host}.png`;
      const screenshotPath = path.join(destination, filename);

      try {
        const response = await page.goto(`https://${host}/`, {
          waitUntil: 'domcontentloaded',
          timeout: 20000
        });

        await page.screenshot({
          path: screenshotPath,
          fullPage: true,
          timeout: 15000
        });

        results.push({
          host,
          status: 'success',
          httpStatus: response?.status() ?? null,
          title: await page.title(),
          screenshotPath
        });

        console.log(`[${i + 1}/${hosts.length}] OK ${host}`);
      } catch (error) {
        results.push({
          host,
          status: 'failed',
          error: error.message
        });

        console.error(`[${i + 1}/${hosts.length}] FAIL ${host}: ${error.message}`);
      } finally {
        await page.close();
      }
    }
  } finally {
    await browser.close();
  }

  await fs.writeFile(
    path.join(destination, 'results.json'),
    JSON.stringify(results, null, 2),
    'utf8'
  );

  return { destination, results };
}

module.exports = { captureHosts, validateTargets };
