const paths = require('./paths');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const webpack = require('webpack');
const TsconfigPathsPlugin = require('tsconfig-paths-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const WorkboxPlugin = require('workbox-webpack-plugin');

module.exports = {
    mode: 'development',

    entry: {
        app: ['@babel/polyfill', paths.appIndex, 'webpack-hot-middleware/client'],
    },

    devtool: 'inline-source-map',

    // Which extensions Webpack will resolve when files import other files
    resolve: {
        extensions: ['.tsx', '.ts', '.js'],
        plugins: [new TsconfigPathsPlugin({ configFile: paths.tsconfig })],
        fallback: {
            url: require.resolve('url/'),
        },
    },

    output: {
        path: paths.appBuild,
        publicPath: '/',
        filename: '[name].[fullhash].js',
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
                        },
                    },
                    'ts-loader',
                ],
                exclude: /node_modules/,
            },
            {
                test: /\.(png|jpe?g)/,
                type: 'asset/resource',
            },
        ],
    },

    plugins: [
        new HtmlWebpackPlugin({ template: paths.appIndexTemplate }),
        new webpack.HotModuleReplacementPlugin(),
        new webpack.DefinePlugin({
            __API__: paths.localDevServerHost,
        }),
        new CopyWebpackPlugin({
            patterns: [
                { from: 'src/assets/resources', to: 'resources' },
                { from: 'src/assets/pwa', to: '.' },
            ],
        }),
        new WorkboxPlugin.GenerateSW({
            // Do not precache images
            exclude: [/\.(?:png|jpg|jpeg|svg)$/],

            // Define runtime caching rules.
            runtimeCaching: [
                {
                    // Match any request that ends with .png, .jpg, .jpeg or .svg.
                    urlPattern: /\.(?:png|jpg|jpeg|svg)$/,

                    // Apply a cache-first strategy.
                    handler: 'CacheFirst',

                    options: {
                        // Use a custom cache name.
                        cacheName: 'images',

                        // Only cache 10 images.
                        expiration: {
                            maxEntries: 10,
                        },
                    },
                },
            ],
        }),
    ],
};
