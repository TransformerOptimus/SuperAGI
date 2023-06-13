"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.cosmiconfig = cosmiconfig;
exports.cosmiconfigSync = cosmiconfigSync;
exports.metaSearchPlaces = exports.defaultLoaders = void 0;

var _os = _interopRequireDefault(require("os"));

var _Explorer = require("./Explorer");

var _ExplorerSync = require("./ExplorerSync");

var _loaders = require("./loaders");

var _types = require("./types");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

/* eslint-disable @typescript-eslint/explicit-module-boundary-types */
// this needs to be hardcoded, as this is intended for end users, who can't supply options at this point
const metaSearchPlaces = ['package.json', '.config.json', '.config.yaml', '.config.yml', '.config.js', '.config.cjs']; // do not allow mutation of default loaders. Make sure it is set inside options

exports.metaSearchPlaces = metaSearchPlaces;
const defaultLoaders = Object.freeze({
  '.cjs': _loaders.loaders.loadJs,
  '.js': _loaders.loaders.loadJs,
  '.json': _loaders.loaders.loadJson,
  '.yaml': _loaders.loaders.loadYaml,
  '.yml': _loaders.loaders.loadYaml,
  noExt: _loaders.loaders.loadYaml
});
exports.defaultLoaders = defaultLoaders;

const identity = function identity(x) {
  return x;
};

function replaceMetaPlaceholders(paths, moduleName) {
  return paths.map(path => path.replace('{name}', moduleName));
}

function getExplorerOptions(moduleName, options) {
  var _metaConfig$config;

  const metaExplorer = new _ExplorerSync.ExplorerSync({
    packageProp: 'cosmiconfig',
    stopDir: process.cwd(),
    searchPlaces: metaSearchPlaces,
    ignoreEmptySearchPlaces: false,
    usePackagePropInConfigFiles: true,
    loaders: defaultLoaders,
    transform: identity,
    cache: true,
    metaConfigFilePath: null
  });
  const metaConfig = metaExplorer.searchSync();

  if (!metaConfig) {
    return normalizeOptions(moduleName, options);
  }

  if ((_metaConfig$config = metaConfig.config) !== null && _metaConfig$config !== void 0 && _metaConfig$config.loaders) {
    throw new Error('Can not specify loaders in meta config file');
  }

  const overrideOptions = metaConfig.config ?? {};

  if (overrideOptions.searchPlaces) {
    overrideOptions.searchPlaces = replaceMetaPlaceholders(overrideOptions.searchPlaces, moduleName);
  }

  overrideOptions.metaConfigFilePath = metaConfig.filepath;
  const mergedOptions = { ...options,
    ...overrideOptions
  };
  return normalizeOptions(moduleName, mergedOptions);
}

function cosmiconfig(moduleName, options = {}) {
  const normalizedOptions = getExplorerOptions(moduleName, options);
  const explorer = new _Explorer.Explorer(normalizedOptions);
  return {
    search: explorer.search.bind(explorer),
    load: explorer.load.bind(explorer),
    clearLoadCache: explorer.clearLoadCache.bind(explorer),
    clearSearchCache: explorer.clearSearchCache.bind(explorer),
    clearCaches: explorer.clearCaches.bind(explorer)
  };
} // eslint-disable-next-line @typescript-eslint/explicit-function-return-type


function cosmiconfigSync(moduleName, options = {}) {
  const normalizedOptions = getExplorerOptions(moduleName, options);
  const explorerSync = new _ExplorerSync.ExplorerSync(normalizedOptions);
  return {
    search: explorerSync.searchSync.bind(explorerSync),
    load: explorerSync.loadSync.bind(explorerSync),
    clearLoadCache: explorerSync.clearLoadCache.bind(explorerSync),
    clearSearchCache: explorerSync.clearSearchCache.bind(explorerSync),
    clearCaches: explorerSync.clearCaches.bind(explorerSync)
  };
}

function normalizeOptions(moduleName, options) {
  const defaults = {
    packageProp: moduleName,
    searchPlaces: ['package.json', `.${moduleName}rc`, `.${moduleName}rc.json`, `.${moduleName}rc.yaml`, `.${moduleName}rc.yml`, `.${moduleName}rc.js`, `.${moduleName}rc.cjs`, `.config/${moduleName}rc`, `.config/${moduleName}rc.json`, `.config/${moduleName}rc.yaml`, `.config/${moduleName}rc.yml`, `.config/${moduleName}rc.js`, `.config/${moduleName}rc.cjs`, `${moduleName}.config.js`, `${moduleName}.config.cjs`],
    ignoreEmptySearchPlaces: true,
    stopDir: _os.default.homedir(),
    cache: true,
    transform: identity,
    loaders: defaultLoaders,
    metaConfigFilePath: null
  };
  let loaders = { ...defaults.loaders
  };

  if (options.loaders) {
    Object.assign(loaders, options.loaders);
  }

  return { ...defaults,
    ...options,
    loaders
  };
}
//# sourceMappingURL=index.js.map