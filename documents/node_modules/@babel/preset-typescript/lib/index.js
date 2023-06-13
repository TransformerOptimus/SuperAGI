'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

var helperPluginUtils = require('@babel/helper-plugin-utils');
var transformTypeScript = require('@babel/plugin-transform-typescript');
require('@babel/plugin-syntax-jsx');
var transformModulesCommonJS = require('@babel/plugin-transform-modules-commonjs');
var helperValidatorOption = require('@babel/helper-validator-option');

function _interopDefaultLegacy (e) { return e && typeof e === 'object' && 'default' in e ? e : { 'default': e }; }

var transformTypeScript__default = /*#__PURE__*/_interopDefaultLegacy(transformTypeScript);
var transformModulesCommonJS__default = /*#__PURE__*/_interopDefaultLegacy(transformModulesCommonJS);

const v = new helperValidatorOption.OptionValidator("@babel/preset-typescript");
function normalizeOptions(options = {}) {
  let {
    allowNamespaces = true,
    jsxPragma,
    onlyRemoveTypeImports
  } = options;
  const TopLevelOptions = {
    ignoreExtensions: "ignoreExtensions",
    allowNamespaces: "allowNamespaces",
    disallowAmbiguousJSXLike: "disallowAmbiguousJSXLike",
    jsxPragma: "jsxPragma",
    jsxPragmaFrag: "jsxPragmaFrag",
    onlyRemoveTypeImports: "onlyRemoveTypeImports",
    optimizeConstEnums: "optimizeConstEnums",
    allExtensions: "allExtensions",
    isTSX: "isTSX"
  };
  const jsxPragmaFrag = v.validateStringOption(TopLevelOptions.jsxPragmaFrag, options.jsxPragmaFrag, "React.Fragment");
  {
    var allExtensions = v.validateBooleanOption(TopLevelOptions.allExtensions, options.allExtensions, false);
    var isTSX = v.validateBooleanOption(TopLevelOptions.isTSX, options.isTSX, false);
    if (isTSX) {
      v.invariant(allExtensions, "isTSX:true requires allExtensions:true");
    }
  }
  const ignoreExtensions = v.validateBooleanOption(TopLevelOptions.ignoreExtensions, options.ignoreExtensions, false);
  const disallowAmbiguousJSXLike = v.validateBooleanOption(TopLevelOptions.disallowAmbiguousJSXLike, options.disallowAmbiguousJSXLike, false);
  if (disallowAmbiguousJSXLike) {
    {
      v.invariant(allExtensions, "disallowAmbiguousJSXLike:true requires allExtensions:true");
    }
  }
  const optimizeConstEnums = v.validateBooleanOption(TopLevelOptions.optimizeConstEnums, options.optimizeConstEnums, false);
  const normalized = {
    ignoreExtensions,
    allowNamespaces,
    disallowAmbiguousJSXLike,
    jsxPragma,
    jsxPragmaFrag,
    onlyRemoveTypeImports,
    optimizeConstEnums
  };
  {
    normalized.allExtensions = allExtensions;
    normalized.isTSX = isTSX;
  }
  return normalized;
}

var index = helperPluginUtils.declarePreset((api, opts) => {
  api.assertVersion(7);
  const {
    allExtensions,
    ignoreExtensions,
    allowNamespaces,
    disallowAmbiguousJSXLike,
    isTSX,
    jsxPragma,
    jsxPragmaFrag,
    onlyRemoveTypeImports,
    optimizeConstEnums
  } = normalizeOptions(opts);
  const pluginOptions = disallowAmbiguousJSXLike => ({
    allowDeclareFields: opts.allowDeclareFields,
    allowNamespaces,
    disallowAmbiguousJSXLike,
    jsxPragma,
    jsxPragmaFrag,
    onlyRemoveTypeImports,
    optimizeConstEnums
  });
  const getPlugins = (isTSX, disallowAmbiguousJSXLike) => {
    {
      return [[transformTypeScript__default["default"], Object.assign({
        isTSX
      }, pluginOptions(disallowAmbiguousJSXLike))]];
    }
  };
  const disableExtensionDetect = allExtensions || ignoreExtensions;
  return {
    overrides: disableExtensionDetect ? [{
      plugins: getPlugins(isTSX, disallowAmbiguousJSXLike)
    }] : [{
      test: /\.ts$/,
      plugins: getPlugins(false, false)
    }, {
      test: /\.mts$/,
      sourceType: "module",
      plugins: getPlugins(false, true)
    }, {
      test: /\.cts$/,
      sourceType: "unambiguous",
      plugins: [[transformModulesCommonJS__default["default"], {
        allowTopLevelThis: true
      }], [transformTypeScript__default["default"], pluginOptions(true)]]
    }, {
      test: /\.tsx$/,
      plugins: getPlugins(true, false)
    }]
  };
});

exports["default"] = index;
//# sourceMappingURL=index.js.map
