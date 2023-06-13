var _Object$defineProperty = require("@babel/runtime-corejs3/core-js/object/define-property");
function _defineAccessor(type, obj, key, fn) {
  var desc = {
    configurable: !0,
    enumerable: !0
  };
  return desc[type] = fn, _Object$defineProperty(obj, key, desc);
}
module.exports = _defineAccessor, module.exports.__esModule = true, module.exports["default"] = module.exports;