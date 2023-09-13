const express = require('express');
const next = require('next');

const dev = process.env.NODE_ENV !== 'production';
const app = next({ dev });
const handle = app.getRequestHandler();
console.log('in express')

app.prepare().then(() => {
    const server = express();

    // Define your Express routes here

    server.get('/login', (req, res) => {
        return app.render(req, res, '/login', req.query);
    });

    server.get('/', (req, res) => {
        return app.render(req, res, '/index', req.query);
    });

    // Handle other routes using Next.js
    server.get('*', (req, res) => {
        return handle(req, res);
    });

});
