const path = require('path');
const fs = require('fs');

const projectDirectory = fs.realpathSync(process.cwd());
const resolveProject = (relativePath) => path.resolve(projectDirectory, relativePath);

module.exports = {
    appBuild: resolveProject('build'),
    appIndex: resolveProject('src/index.tsx'),
    appIndexTemplate: resolveProject('public/index.html'),
    webpackConfig: resolveProject('config/webpack.config.js')
};
