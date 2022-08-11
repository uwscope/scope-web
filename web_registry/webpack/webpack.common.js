const paths = require('./paths');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const webpack = require('webpack');
const TsconfigPathsPlugin = require('tsconfig-paths-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = {
    entry: {
        app: ['@babel/polyfill', paths.appIndex],
    },

    // Extensions Webpack will resolve when files import other files
    resolve: {
        extensions: ['.tsx', '.ts', '.js'],
        plugins: [new TsconfigPathsPlugin({ configFile: paths.tsconfig })],
    },

    output: {
        publicPath: '/',
        filename: '[name].[fullhash].js',
    },

    module: {
        rules: [
            // Primary Typescript loader, loading .tsx or .ts
            {
                test: /\.tsx?$/,
                use: [
                    {
                        loader: 'babel-loader',
                        options: {
                            presets: ['@babel/env', '@babel/react'],
                        },
                    },
                    'ts-loader',
                ],
                exclude: /node_modules/,
            },
            // Image resources
            {
                test: /\.(jpe?g|png|gif|svg)$/i,
                type: 'asset/resource',
            },
        ],
    },

    externals: {
        clientConfig: 'clientConfig',
    },

    plugins: [
        new HtmlWebpackPlugin({
            template: paths.appIndexTemplate,
        }),
        new CopyWebpackPlugin({
            patterns: [{ from: 'config', to: 'config' }],
        }),
        new CopyWebpackPlugin({
            patterns: [{ from: 'src/assets/resources', to: 'resources' }],
        }),
        new CopyWebpackPlugin({
            patterns: [{ from: 'src/assets/pwa', to: '' }],
        }),
    ],
};
