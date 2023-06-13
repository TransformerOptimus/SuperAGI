"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getErrorCausalChain = void 0;
function getErrorCausalChain(error) {
    if (error.cause) {
        return [error, ...getErrorCausalChain(error.cause)];
    }
    return [error];
}
exports.getErrorCausalChain = getErrorCausalChain;
//# sourceMappingURL=errorUtils.js.map