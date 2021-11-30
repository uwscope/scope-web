const rimraf = require('rimraf');
const webpack = require('webpack');

const paths = require('../config/paths');
const webpackConfig = require(paths.webpackConfig);

const compiler = webpack(webpackConfig);

rimraf.sync(paths.appBuild);
compiler.run();
