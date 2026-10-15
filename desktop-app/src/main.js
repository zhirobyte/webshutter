const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('node:path');
const fs = require('node:fs/promises');
const { discover } = require('./discovery');
const { captureHosts } = require('./capture');

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    backgroundColor: '#101827',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true
    }
  });

  win.loadFile(path.join(__dirname, 'index.html'));
  win.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
}

app.whenReady().then(() => {
  ipcMain.handle('capture:run', async (_event, hosts) => {
    return captureHosts(hosts);
  });

  ipcMain.handle('discovery:run', async (_event, domain) => {
    return discover(domain);
  });

  ipcMain.handle('discovery:export', async (_event, hosts) => {
    if (
      !Array.isArray(hosts) ||
      hosts.length > 100000 ||
      hosts.some(h => typeof h !== 'string' || h.length > 253)
    ) {
      throw new Error('Invalid hostname list');
    }

    const result = await dialog.showSaveDialog({
      title: 'Export discovered hostnames',
      defaultPath: 'discovered-hosts.txt',
      filters: [{ name: 'Text files', extensions: ['txt'] }]
    });

    if (result.canceled || !result.filePath) {
      return { saved: false };
    }

    await fs.writeFile(
      result.filePath,
      hosts.join('\n') + (hosts.length ? '\n' : ''),
      'utf8'
    );

    return { saved: true };
  });

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
