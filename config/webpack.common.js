const paths = require('./paths');
const HtmlWebpackPlugin = require('html-webpack-plugin')
const webpack = require('webpack');
const TsconfigPathsPlugin = require('tsconfig-paths-webpack-plugin');

module.exports = {
    entry: {
        app: ['@babel/polyfill', paths.appIndex]
    },

    // Extensions Webpack will resolve when files import other files
    resolve: {
        extensions: [
            '.tsx', '.ts', '.js'
        ],
        plugins: [new TsconfigPathsPlugin({ configFile: paths.tsconfig})]
    },

    output: {
        publicPath: "/",
        filename: '[name].[fullhash].js'
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
                        }
                    },
                    'ts-loader'
                ],
                exclude: /node_modules/,
            },
            // Image resources
            {
                test: /\.png/,
                type: 'asset/resource',
            },
        ]
    },

    plugins: [
        new HtmlWebpackPlugin({ template: paths.appIndexTemplate }),
        // TODO resolve server paths in dev/prod
        new webpack.DefinePlugin({
            __API__: paths.localDevServerHost
        })
    ],
}
