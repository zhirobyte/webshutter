const { captureHosts } = require('../src/capture');
const path = require('node:path');

(async () => {
  const outputDir = path.join(__dirname, '..', 'test-results', 'capture-module');

  const result = await captureHosts(
    ['example.com'],
    outputDir
  );

  console.log(JSON.stringify(result, null, 2));

  if (result.results[0]?.status !== 'success') {
    process.exitCode = 1;
  }
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
