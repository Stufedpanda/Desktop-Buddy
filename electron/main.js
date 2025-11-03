// main.js
const { app, BrowserWindow } = require('electron');
const path = require('path');
const http = require('http');
const fs = require('fs');
const mime = require('mime-types');

const { spawn } = require('child_process');
const waitPort = require('wait-port');
const kill = require('tree-kill');

let win, server, pyProc;

// py server

const pyScript = path.join(__dirname, 'startserver.py');
const py = 'python';
const pyHost = '127.0.0.1';
const pyPort = 5000;

function startServer(cb) {
  const root = __dirname;
  server = http.createServer((req, res) => {
    let urlPath = (req.url || '/').split('?')[0];
    if (urlPath === '/') urlPath = '/index.html';
    const filePath = path.join(root, urlPath);

    fs.readFile(filePath, (err, data) => {
      if (err) { res.writeHead(404); return res.end('Not found: ' + filePath); }

      // mime-types returns e.g. 'text/html; charset=utf-8'
      const ct = mime.contentType(filePath) || 'application/octet-stream';
      res.setHeader('Content-Type', ct);
      res.end(data);
    });
  }).listen(0, '127.0.0.1', () => cb(server.address().port));
}

function createWindow(port) {
  win = new BrowserWindow({
    width: 900, height: 1000,
    frame: true, transparent: false, backgroundColor: '#202020',
    webPreferences: { contextIsolation: true, nodeIntegration: false }
  });

  win.loadURL(`http://127.0.0.1:${port}/index.html`);

  // lock zoom at 100% so DevTools doesn’t change CSS pixels
  win.webContents.setVisualZoomLevelLimits(1, 1);
  win.webContents.on('did-finish-load', () => {
    win.webContents.setZoomFactor(1);
  });

  // optional while debugging; you can comment this out later
  win.webContents.openDevTools({ mode: 'detach' });
}

async function boot() {
  const args = [pyScript];
  pyProc = spawn(py, args, { cwd: __dirname, env: process.env });

  // console logs for debugging
  pyProc.stdout.on('data', d => console.log('[py]', d.toString().trim()));
  pyProc.stderr.on('data', d => console.error('[py]', d.toString().trim()));
  pyProc.on('exit', code => console.log(`[py] exited with code ${code}`));

  await waitPort({ host: pyHost, port: pyPort, timeout: 2000 });
  startServer(createWindow);
}

app.whenReady().then(boot)
app.on('window-all-closed', () => {
  server?.close();
  if (pyProc && !pyProc.killed) kill(pyProc.pid);
  app.quit();
});

app.on('before-quit', () => {
  if (pyProc && !pyProc.killed) kill(pyProc.pid);
});