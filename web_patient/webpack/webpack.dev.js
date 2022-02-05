const paths = require('./paths');
const webpack = require('webpack');

const { merge } = require('webpack-merge');
const common = require('./webpack.common.js');

module.exports = merge(common, {
    mode: 'development',
    devtool: 'inline-source-map',

    entry: {
        app: ['webpack-hot-middleware/client'],
    },

    output: {
        path: paths.appBuildDev,
    },

    plugins: [
        // Hot loading
        new webpack.HotModuleReplacementPlugin(),
    ],
});
