const express = require('express');

const paths = require('../config/paths');

console.log(`Serving from production build in ${paths.appBuildProd}.`);

const app = express();

app.use(express.static(paths.appBuildProd));

port = 3000;
app.listen(port, function () {
        console.log(`Listening on http://localhost:${port}/.`);
    }
);
