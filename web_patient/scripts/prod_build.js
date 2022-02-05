const rimraf = require('rimraf');
const webpack = require('webpack');
const paths = require('../webpack/paths');
const webpackConfig = require(paths.webpackConfigProd);
const fs = require('fs');

console.log(`Building production in ${paths.appBuildProd}.`);

rimraf.sync(paths.appBuildProd);

const compiler = webpack(webpackConfig);
compiler.run((err, stats) => {
    console.log(stats.toString({ chunks: false, colors: true }), '\n\n');

    if (err || stats.hasErrors()) {
        console.error('\x1b[31m%s\x1b[0m', 'BUILD ERROR', 'Build failed');

        if (err) {
            console.error(err.stack || err);

            if (err.details) {
                console.error(err.details);
            }
        }
        return;
    } else {
        if (fs.existsSync(paths.appBuildProd)) {
            console.log('\x1b[32m%s\x1b[0m', 'BUILD COMPLETED', `Build directory found at ${paths.appBuildProd}`);
        } else {
            console.error('\x1b[31m%s\x1b[0m', 'BUILD ERROR', `Build directory not found at ${paths.appBuildProd}`);
        }
    }

    compiler.close((closeErr) => {
        // ...
    });
});
