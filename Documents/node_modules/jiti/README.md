# jiti

> Runtime typescript and ESM support for Node.js

[![version][npm-v-src]][npm-v-href]
[![downloads][npm-d-src]][npm-d-href]
[![size][size-src]][size-href]

## Features

- Seamless typescript and ESM syntax support
- Seamless interoperability between ESM and CommonJS
- Synchronous API to replace `require`
- Super slim and zero dependency
- Smart syntax detection to avoid extra transforms
- CommonJS cache integration
- Filesystem transpile hard cache
- V8 compile cache
- Custom resolve alias

## Usage

### Programmatic

```js
const jiti = require("jiti")(__filename);

jiti("./path/to/file.ts");
```

You can also pass options as second argument:

```js
const jiti = require("jiti")(__filename, { debug: true });
```

### CLI

```bash
jiti index.ts
# or npx jiti index.ts
```

### Register require hook

```bash
node -r jiti/register index.ts
```

Alternatively, you can register `jiti` as a require hook programmatically:

```js
const jiti = require("jiti")();
const unregister = jiti.register();
```

## Options

### `debug`

- Type: Boolean
- Default: `false`
- Environment Variable: `JITI_DEBUG`

Enable debug to see which files are transpiled

### `cache`

- Type: Boolean | String
- Default: `true`
- Environment Variable: `JITI_CACHE`

Use transpile cache

If set to `true` will use `node_modules/.cache/jiti` (if exists) or `{TMP_DIR}/node-jiti`

### `esmResolve`

- Type: Boolean | String
- Default: `false`
- Environment Variable: `JITI_ESM_RESOLVE`

Using esm resolution algorithm to support `import` condition.

### `transform`

- Type: Function
- Default: Babel (lazy loaded)

Transform function. See [src/babel](./src/babel.ts) for more details

### `sourceMaps`

- Type: Boolean
- Default `false`
- Environment Variable: `JITI_SOURCE_MAPS`

Add inline source map to transformed source for better debugging.

### `interopDefault`

- Type: Boolean
- Default: `false`

Return the `.default` export of a module at the top-level.

### `alias`

- Type: Object
- Default: -
- Environment Variable: `JITI_ALIAS`

Custom alias map used to resolve ids.

### `nativeModules`

- Type: Array
- Default: ['typescript`]
- Environment Variable: `JITI_NATIVE_MODULES`

List of modules (within `node_modules`) to always use native require for them.

### `transformModules`

- Type: Array
- Default: []
- Environment Variable: `JITI_TRANSFORM_MODULES`

List of modules (within `node_modules`) to transform them regardless of syntax.

## Development

- Clone this repository
- Enable [Corepack](https://github.com/nodejs/corepack) using `corepack enable`
- Install dependencies using `pnpm install`
- Run `pnpm dev`
- Run `pnpm jiti ./test/path/to/file.ts`

## License

MIT. Made with 💖

<!-- Refs -->

[npm-v-src]: https://img.shields.io/npm/v/jiti?style=flat-square
[npm-v-href]: https://npmjs.com/package/jiti
[npm-d-src]: https://img.shields.io/npm/dm/jiti?style=flat-square
[npm-d-href]: https://npmjs.com/package/jiti
[github-actions-src]: https://img.shields.io/github/workflow/status/unjs/jiti/ci/master?style=flat-square
[github-actions-href]: https://github.com/unjs/jiti/actions?query=workflow%3Aci
[size-src]: https://packagephobia.now.sh/badge?p=jiti
[size-href]: https://packagephobia.now.sh/result?p=jiti
