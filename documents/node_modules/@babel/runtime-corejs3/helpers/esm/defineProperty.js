import _Object$defineProperty from "@babel/runtime-corejs3/core-js/object/define-property";
import toPropertyKey from "./toPropertyKey.js";
export default function _defineProperty(obj, key, value) {
  key = toPropertyKey(key);
  if (key in obj) {
    _Object$defineProperty(obj, key, {
      value: value,
      enumerable: true,
      configurable: true,
      writable: true
    });
  } else {
    obj[key] = value;
  }
  return obj;
}