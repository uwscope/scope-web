const paths = require('./paths');
const HtmlWebpackPlugin = require('html-webpack-plugin')
const webpack = require('webpack');

module.exports = {
    mode: "development",

    entry: {
        app: [ paths.appIndex, 'webpack-hot-middleware/client' ]
    },

    // Which extensions Webpack will resolve when files import other files
    resolve: {
        extensions: [
            '.tsx', '.ts', '.jsx', '.js'
        ]
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
                ]
            }
        ]
    },

    plugins: [
        new HtmlWebpackPlugin({ template: paths.appIndexTemplate }),
        new webpack.HotModuleReplacementPlugin(),
    ],
}
