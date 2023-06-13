"use strict";
/**
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getErrorCausalChain = exports.applyTrailingSlash = exports.blogPostContainerID = void 0;
// __ prefix allows search crawlers (Algolia/DocSearch) to ignore anchors
// https://github.com/facebook/docusaurus/issues/8883#issuecomment-1516328368
exports.blogPostContainerID = '__blog-post-container';
var applyTrailingSlash_1 = require("./applyTrailingSlash");
Object.defineProperty(exports, "applyTrailingSlash", { enumerable: true, get: function () { return __importDefault(applyTrailingSlash_1).default; } });
var errorUtils_1 = require("./errorUtils");
Object.defineProperty(exports, "getErrorCausalChain", { enumerable: true, get: function () { return errorUtils_1.getErrorCausalChain; } });
//# sourceMappingURL=index.js.map