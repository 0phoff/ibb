"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.area_polygon = exports.inside_polygon = exports.centroid_polygon = exports.serialize_numpy = exports.deserialize_numpy = void 0;
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
function centroid_polygon(coords) {
    const centroid = [0, 0];
    for (const [x, y] of coords) {
        centroid[0] += x;
        centroid[1] += y;
    }
    centroid[0] /= coords.length;
    centroid[1] /= coords.length;
    return centroid;
}
exports.centroid_polygon = centroid_polygon;
;
function inside_polygon(point, coords) {
    // ray-casting algorithm based on
    // https://wrf.ecse.rpi.edu/Research/Short_Notes/pnpoly.html/pnpoly.html
    var x = point[0], y = point[1];
    var inside = false;
    for (var i = 0, j = coords.length - 1; i < coords.length; j = i++) {
        var xi = coords[i][0], yi = coords[i][1];
        var xj = coords[j][0], yj = coords[j][1];
        var intersect = ((yi > y) != (yj > y))
            && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
        if (intersect)
            inside = !inside;
    }
    return inside;
}
exports.inside_polygon = inside_polygon;
;
function area_polygon(coords) {
    var area = 0;
    for (let i = 0, j = coords.length - 1; i < coords.length; i++) {
        area += (coords[j][0] + coords[i][0]) * Math.abs(coords[j][1] - coords[i][1]);
        j = i;
    }
    return Math.abs(area / 2);
}
exports.area_polygon = area_polygon;
;
//# sourceMappingURL=util.js.map