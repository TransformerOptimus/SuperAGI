"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.Explorer = void 0;

var _path = _interopRequireDefault(require("path"));

var _cacheWrapper = require("./cacheWrapper");

var _ExplorerBase = require("./ExplorerBase");

var _getDirectory = require("./getDirectory");

var _readFile = require("./readFile");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class Explorer extends _ExplorerBase.ExplorerBase {
  constructor(options) {
    super(options);
  }

  async search(searchFrom = process.cwd()) {
    if (this.config.metaConfigFilePath) {
      const config = await this._loadFile(this.config.metaConfigFilePath, true);

      if (config && !config.isEmpty) {
        return config;
      }
    }

    return await this.searchFromDirectory(await (0, _getDirectory.getDirectory)(searchFrom));
  }

  async searchFromDirectory(dir) {
    const absoluteDir = _path.default.resolve(process.cwd(), dir);

    const run = async () => {
      const result = await this.searchDirectory(absoluteDir);
      const nextDir = this.nextDirectoryToSearch(absoluteDir, result);

      if (nextDir) {
        return this.searchFromDirectory(nextDir);
      }

      return await this.config.transform(result);
    };

    if (this.searchCache) {
      return (0, _cacheWrapper.cacheWrapper)(this.searchCache, absoluteDir, run);
    }

    return run();
  }

  async searchDirectory(dir) {
    for await (const place of this.config.searchPlaces) {
      const placeResult = await this.loadSearchPlace(dir, place);

      if (this.shouldSearchStopWithResult(placeResult)) {
        return placeResult;
      }
    } // config not found


    return null;
  }

  async loadSearchPlace(dir, place) {
    const filepath = _path.default.join(dir, place);

    const fileContents = await (0, _readFile.readFile)(filepath);
    return await this.createCosmiconfigResult(filepath, fileContents, false);
  }

  async loadFileContent(filepath, content) {
    if (content === null) {
      return null;
    }

    if (content.trim() === '') {
      return undefined;
    }

    const loader = this.getLoaderEntryForFile(filepath);

    try {
      return await loader(filepath, content);
    } catch (e) {
      e.filepath = filepath;
      throw e;
    }
  }

  async createCosmiconfigResult(filepath, content, forceProp) {
    const fileContent = await this.loadFileContent(filepath, content);
    return this.loadedContentToCosmiconfigResult(filepath, fileContent, forceProp);
  }

  async load(filepath) {
    return this._loadFile(filepath, false);
  }

  async _loadFile(filepath, forceProp) {
    this.validateFilePath(filepath);

    const absoluteFilePath = _path.default.resolve(process.cwd(), filepath);

    const runLoad = async () => {
      const fileContents = await (0, _readFile.readFile)(absoluteFilePath, {
        throwNotFound: true
      });
      const result = await this.createCosmiconfigResult(absoluteFilePath, fileContents, forceProp);
      return await this.config.transform(result);
    };

    if (this.loadCache) {
      return (0, _cacheWrapper.cacheWrapper)(this.loadCache, absoluteFilePath, runLoad);
    }

    return runLoad();
  }

}

exports.Explorer = Explorer;
//# sourceMappingURL=Explorer.js.map