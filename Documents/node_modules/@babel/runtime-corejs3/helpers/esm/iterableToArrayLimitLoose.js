import _Symbol from "@babel/runtime-corejs3/core-js/symbol";
import _getIteratorMethod from "@babel/runtime-corejs3/core-js/get-iterator-method";
export default function _iterableToArrayLimitLoose(arr, i) {
  var _i = arr && ("undefined" != typeof _Symbol && _getIteratorMethod(arr) || arr["@@iterator"]);
  if (null != _i) {
    var _s,
      _arr = [];
    for (_i = _i.call(arr); arr.length < i && !(_s = _i.next()).done;) _arr.push(_s.value);
    return _arr;
  }
}