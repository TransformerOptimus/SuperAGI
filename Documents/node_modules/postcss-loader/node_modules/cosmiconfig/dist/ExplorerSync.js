"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.ExplorerSync = void 0;

var _path = _interopRequireDefault(require("path"));

var _cacheWrapper = require("./cacheWrapper");

var _ExplorerBase = require("./ExplorerBase");

var _getDirectory = require("./getDirectory");

var _readFile = require("./readFile");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class ExplorerSync extends _ExplorerBase.ExplorerBase {
  constructor(options) {
    super(options);
  }

  searchSync(searchFrom = process.cwd()) {
    if (this.config.metaConfigFilePath) {
      const config = this._loadFileSync(this.config.metaConfigFilePath, true);

      if (config && !config.isEmpty) {
        return config;
      }
    }

    return this.searchFromDirectorySync((0, _getDirectory.getDirectorySync)(searchFrom));
  }

  searchFromDirectorySync(dir) {
    const absoluteDir = _path.default.resolve(process.cwd(), dir);

    const run = () => {
      const result = this.searchDirectorySync(absoluteDir);
      const nextDir = this.nextDirectoryToSearch(absoluteDir, result);

      if (nextDir) {
        return this.searchFromDirectorySync(nextDir);
      }

      return this.config.transform(result);
    };

    if (this.searchCache) {
      return (0, _cacheWrapper.cacheWrapperSync)(this.searchCache, absoluteDir, run);
    }

    return run();
  }

  searchDirectorySync(dir) {
    for (const place of this.config.searchPlaces) {
      const placeResult = this.loadSearchPlaceSync(dir, place);

      if (this.shouldSearchStopWithResult(placeResult)) {
        return placeResult;
      }
    } // config not found


    return null;
  }

  loadSearchPlaceSync(dir, place) {
    const filepath = _path.default.join(dir, place);

    const content = (0, _readFile.readFileSync)(filepath);
    return this.createCosmiconfigResultSync(filepath, content, false);
  }

  loadFileContentSync(filepath, content) {
    if (content === null) {
      return null;
    }

    if (content.trim() === '') {
      return undefined;
    }

    const loader = this.getLoaderEntryForFile(filepath);

    try {
      return loader(filepath, content);
    } catch (e) {
      e.filepath = filepath;
      throw e;
    }
  }

  createCosmiconfigResultSync(filepath, content, forceProp) {
    const fileContent = this.loadFileContentSync(filepath, content);
    return this.loadedContentToCosmiconfigResult(filepath, fileContent, forceProp);
  }

  loadSync(filepath) {
    return this._loadFileSync(filepath, false);
  }

  _loadFileSync(filepath, forceProp) {
    this.validateFilePath(filepath);

    const absoluteFilePath = _path.default.resolve(process.cwd(), filepath);

    const runLoadSync = () => {
      const content = (0, _readFile.readFileSync)(absoluteFilePath, {
        throwNotFound: true
      });
      const cosmiconfigResult = this.createCosmiconfigResultSync(absoluteFilePath, content, forceProp);
      return this.config.transform(cosmiconfigResult);
    };

    if (this.loadCache) {
      return (0, _cacheWrapper.cacheWrapperSync)(this.loadCache, absoluteFilePath, runLoadSync);
    }

    return runLoadSync();
  }

}

exports.ExplorerSync = ExplorerSync;
//# sourceMappingURL=ExplorerSync.js.map