import _Object$defineProperty from "@babel/runtime-corejs3/core-js/object/define-property";
export default function _defineAccessor(type, obj, key, fn) {
  var desc = {
    configurable: !0,
    enumerable: !0
  };
  return desc[type] = fn, _Object$defineProperty(obj, key, desc);
}