const express = require('express');
const next = require('next');

const dev = process.env.NODE_ENV !== 'DEV';
const app = next({ dev });
const handle = app.getRequestHandler();

app.prepare().then(() => {
  const server = express();

  // Custom route to serve the login page as the root route
  server.get('/', (req, res) => {
    const actualPage = '/login';
    app.render(req, res, actualPage);
  });

  server.get('*', (req, res) => {
    return handle(req, res);
  });

  server.listen(3000, (err) => {
    if (err) throw err;
    console.log('> Ready on http://localhost:3000');
  });
});
