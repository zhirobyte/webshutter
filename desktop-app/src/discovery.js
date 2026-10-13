const https = require('node:https');

const HOST_RE =
  /^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$/;

function validateDomain(input) {
  const domain = String(input || '').trim().toLowerCase().replace(/\.$/, '');

  const labels = domain.split('.');
  const tld = labels[labels.length - 1];

  if (
    !HOST_RE.test(domain) ||
    !/^[a-z]{2,63}$/.test(tld)
  ) {
    throw new Error('Enter a valid root domain, such as example.com');
  }

  return domain;
}

function fetchText(url) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, {
      timeout: 45000,
      headers: { 'User-Agent': 'WebShutter/0.1' }
    }, response => {
      if (response.statusCode !== 200) {
        response.resume();
        reject(new Error(`Discovery API returned HTTP ${response.statusCode}`));
        return;
      }

      let body = '';

      response.setEncoding('utf8');

      response.on('data', chunk => {
        body += chunk;

        if (body.length > 20 * 1024 * 1024) {
          req.destroy(new Error('Discovery response exceeds 20 MB'));
        }
      });

      response.on('end', () => resolve(body));
      response.on('error', reject);
    });

    req.on('timeout', () => {
      req.destroy(new Error('Discovery request timed out'));
    });

    req.on('error', reject);
  });
}

async function discover(domainInput) {
  const domain = validateDomain(domainInput);

  const url = new URL('https://crt.name/v1/search');
  url.searchParams.set('apex', domain);

  const response = await fetchText(url);

  const hosts = new Set();

  for (const line of response.split(/\r?\n/)) {
    let host = line.trim().toLowerCase().replace(/\.$/, '');

    if (host.startsWith('*.')) {
      host = host.slice(2);
    }

    if (
      HOST_RE.test(host) &&
      (host === domain || host.endsWith(`.${domain}`))
    ) {
      hosts.add(host);
    }
  }

  return {
    domain,
    hosts: [...hosts].sort()
  };
}

module.exports = { discover, validateDomain };
