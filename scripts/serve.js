const express = require('express');

const path = require('path');
const paths = require('../config/paths');

console.log(`Serving from production build in ${paths.appBuildProd}.`);

const app = express();

app.use(express.static(paths.appBuildProd));

// This allows redirecting to home to handle routing
app.get('/*', function (req, res) {
    res.sendFile(path.join(paths.appBuild, 'index.html'));
});

port = 3000;
app.listen(port, function () {
    console.log(`Listening on http://localhost:${port}/.`);
});
