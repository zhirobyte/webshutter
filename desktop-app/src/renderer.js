const domainInput = document.getElementById('domain');
const discoverButton = document.getElementById('discover');
const exportButton = document.getElementById('export');
const status = document.getElementById('status');
const results = document.getElementById('results');
const count = document.getElementById('count');
const filter = document.getElementById('filter');
const hostList = document.getElementById('host-list');

let hosts = [];

function renderHosts() {
  const query = filter.value.trim().toLowerCase();
  const filtered = hosts.filter(host => host.includes(query));

  count.textContent =
    `${filtered.length.toLocaleString()} shown / ${hosts.length.toLocaleString()} discovered`;

  hostList.replaceChildren();

  const fragment = document.createDocumentFragment();

  for (const host of filtered.slice(0, 500)) {
    const row = document.createElement('div');
    row.className = 'host-row';
    row.textContent = host;
    fragment.appendChild(row);
  }

  hostList.appendChild(fragment);

  if (filtered.length > 500) {
    const note = document.createElement('p');
    note.textContent = 'Showing the first 500 matches. Use the filter to narrow results.';
    hostList.appendChild(note);
  }
}

discoverButton.addEventListener('click', async () => {
  discoverButton.disabled = true;
  results.hidden = true;
  hosts = [];
  status.textContent = 'Discovering hostnames...';

  try {
    const data = await window.webshutter.discover(domainInput.value);
    hosts = data.hosts;
    filter.value = '';
    results.hidden = false;
    renderHosts();
    status.textContent =
      `Discovery complete: ${hosts.length.toLocaleString()} unique hostnames.`;
  } catch (error) {
    status.textContent = `Error: ${error.message}`;
  } finally {
    discoverButton.disabled = false;
  }
});

filter.addEventListener('input', renderHosts);

exportButton.addEventListener('click', async () => {
  try {
    const result = await window.webshutter.exportHosts(hosts);
    if (result.saved) status.textContent = 'Hostnames exported successfully.';
  } catch (error) {
    status.textContent = `Export failed: ${error.message}`;
  }
});
