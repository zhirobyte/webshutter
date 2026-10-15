const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('webshutter', {
  discover: domain => ipcRenderer.invoke('discovery:run', domain),
  capture: hosts => ipcRenderer.invoke('capture:run', hosts),
  exportHosts: hosts => ipcRenderer.invoke('discovery:export', hosts)
});
