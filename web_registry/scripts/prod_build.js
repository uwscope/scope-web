const rimraf = require('rimraf');
const webpack = require('webpack');
const paths = require('../webpack/paths');
const webpackConfig = require(paths.webpackConfigProd);

console.log(`Building production in ${paths.appBuildProd}.`);

rimraf.sync(paths.appBuildProd);

const compiler = webpack(webpackConfig);
compiler.run();
