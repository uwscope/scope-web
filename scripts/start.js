const express = require('express');
const rimraf = require('rimraf');
const webpack = require('webpack');
const webpackDevMiddleware = require('webpack-dev-middleware');
const webpackHotMiddleware = require('webpack-hot-middleware');

const paths = require('../config/paths');
const webpackConfig = require(paths.webpackConfigDev);

console.log(`Starting debug build with hot reloading.`);

const app = express();
const compiler = webpack(webpackConfig);

rimraf.sync(paths.appBuildDev);

app.use(
    webpackDevMiddleware(compiler, {
        publicPath: webpackConfig.output.publicPath,
        writeToDisk: true
    })
);

app.use(webpackHotMiddleware(compiler));

port = 3000
app.listen(port, function () {
        console.log(`Listening on http://localhost:${port}/.`);
    }
);
