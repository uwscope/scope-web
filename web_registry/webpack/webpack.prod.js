const paths = require('./paths');
const webpack = require('webpack');

const { merge } = require('webpack-merge');
const common = require('./webpack.common.js');

module.exports = merge(common, {
    mode: 'production',
    devtool: 'source-map',

    // Disable minification for easier debugging
    optimization: {
        minimize: false,
    },

    output: {
        path: paths.appBuildProd,
    },

    plugins: [
    ],
});
