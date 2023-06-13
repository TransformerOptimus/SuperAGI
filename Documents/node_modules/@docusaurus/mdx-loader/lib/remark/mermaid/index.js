"use strict";
/**
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
Object.defineProperty(exports, "__esModule", { value: true });
const tslib_1 = require("tslib");
const unist_util_visit_1 = tslib_1.__importDefault(require("unist-util-visit"));
// TODO: this plugin shouldn't be in the core MDX loader
// After we allow plugins to provide Remark/Rehype plugins (see
// https://github.com/facebook/docusaurus/issues/6370), this should be provided
// by theme-mermaid itself
function plugin() {
    return (root) => {
        (0, unist_util_visit_1.default)(root, 'code', (node, index, parent) => {
            if (node.lang === 'mermaid') {
                parent.children.splice(index, 1, {
                    type: 'mermaidCodeBlock',
                    data: {
                        hName: 'mermaid',
                        hProperties: {
                            value: node.value,
                        },
                    },
                });
            }
        });
    };
}
exports.default = plugin;
//# sourceMappingURL=index.js.map