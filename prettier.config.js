const prettierConfig = {
  plugins: [
    "@ianvs/prettier-plugin-sort-imports",
    "prettier-plugin-packagejson",
  ],

  importOrder: [
    "",
    // React
    "^react$",
    "",
    // Node.js built-in modules.
    "<BUILTIN_MODULES>",
    "",
    // Imports not matched by other special words or groups.
    "<THIRD_PARTY_MODULES>",
    "",
    // Relative imports.
    "^[.]",
  ],
  importOrderParserPlugins: ["typescript", "jsx", "decorators"],
  importOrderTypeScriptVersion: "5.0.0",
};

module.exports = prettierConfig;
