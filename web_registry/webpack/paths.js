const path = require('path');
const fs = require('fs');

const projectDirectory = fs.realpathSync(process.cwd());
const resolveProject = (relativePath) => path.resolve(projectDirectory, relativePath);

module.exports = {
    appBuildDev: resolveProject('build'),
    appBuildProd: resolveProject('dist'),
    appIndex: resolveProject('src/index.tsx'),
    appIndexTemplate: resolveProject('public/index.html'),
    tsconfig: resolveProject('tsconfig.json'),
    webpackConfigDev: resolveProject('webpack/webpack.dev.js'),
    webpackConfigProd: resolveProject('webpack/webpack.prod.js'),
};
