const paths = require('./paths');
const HtmlWebpackPlugin = require('html-webpack-plugin')
const webpack = require('webpack');
const TsconfigPathsPlugin = require('tsconfig-paths-webpack-plugin');

module.exports = {
    mode: "development",

    entry: {
        app: ['@babel/polyfill', paths.appIndex, 'webpack-hot-middleware/client' ]
    },

    devtool: 'inline-source-map',

    // Which extensions Webpack will resolve when files import other files
    resolve: {
        extensions: [
            '.tsx', '.ts', '.js'
        ],
        plugins: [new TsconfigPathsPlugin({ configFile: paths.tsconfig})]
    },

    output: {
        path: paths.appBuild,
        publicPath: "/",
        filename: '[name].[fullhash].js'
    },

    module: {
        rules: [
            // Our primary Typescript loader, loading .tsx or .ts
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
            {
                test: /\.png/,
                type: 'asset/resource',
            },
        ]
    },

    plugins: [
        new HtmlWebpackPlugin({ template: paths.appIndexTemplate }),
        new webpack.HotModuleReplacementPlugin(),
    ],
}
