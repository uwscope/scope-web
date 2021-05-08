const paths = require('./paths');
const webpack = require('webpack');

const { merge } = require('webpack-merge');
const common = require('./webpack.common.js');

module.exports = merge(common, {
    mode: 'production',
    devtool: 'source-map',

    output: {
        path: paths.appBuildProd
    },

    plugins: [
        // Local execution of the app server
        new webpack.DefinePlugin({
            __API__: paths.appServerProd
        }),
    ],
});
