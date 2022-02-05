const rimraf = require('rimraf');
const webpack = require('webpack');
const paths = require('../webpack/paths');
const webpackConfig = require(paths.webpackConfigProd);
const fs = require('fs');

console.log(`Building production in ${paths.appBuildProd}.`);

rimraf.sync(paths.appBuildProd);

const compiler = webpack(webpackConfig);
compiler.run((err, stats) => {
    if (err) {
        console.error(err);
        return;
    } else {
        console.log(
            stats.toString({
                colors: true,
            })
        );
    }
});
