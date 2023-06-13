var _Symbol = require("@babel/runtime-corejs3/core-js/symbol");
var _getIteratorMethod = require("@babel/runtime-corejs3/core-js/get-iterator-method");
function _iterableToArrayLimitLoose(arr, i) {
  var _i = arr && ("undefined" != typeof _Symbol && _getIteratorMethod(arr) || arr["@@iterator"]);
  if (null != _i) {
    var _s,
      _arr = [];
    for (_i = _i.call(arr); arr.length < i && !(_s = _i.next()).done;) _arr.push(_s.value);
    return _arr;
  }
}
module.exports = _iterableToArrayLimitLoose, module.exports.__esModule = true, module.exports["default"] = module.exports;