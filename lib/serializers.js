"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.serialize_numpy = exports.deserialize_numpy = void 0;
function deserialize_numpy(data) {
    if (data == null)
        return null;
    return {
        data: new Uint8ClampedArray(data.data.buffer),
        shape: data.shape,
    };
}
exports.deserialize_numpy = deserialize_numpy;
function serialize_numpy(data) {
    return data;
}
exports.serialize_numpy = serialize_numpy;
//# sourceMappingURL=serializers.js.map