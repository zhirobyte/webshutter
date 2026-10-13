const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('webshutter', {
  discover: domain => ipcRenderer.invoke('discovery:run', domain),
  exportHosts: hosts => ipcRenderer.invoke('discovery:export', hosts)
});
