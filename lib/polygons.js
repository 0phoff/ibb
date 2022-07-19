"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.area_polygon = exports.inside_polygon = exports.centroid_polygon = void 0;
function centroid_polygon(polygon) {
    const centroid = [0, 0];
    const { coords } = polygon;
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
function inside_polygon(point, polygon) {
    // ray-casting algorithm based on
    // https://wrf.ecse.rpi.edu/Research/Short_Notes/pnpoly.html/pnpoly.html
    const x = point[0], y = point[1];
    const { coords } = polygon;
    var inside = false;
    for (let i = 0, j = coords.length - 1; i < coords.length; j = i++) {
        const xi = coords[i][0], yi = coords[i][1];
        const xj = coords[j][0], yj = coords[j][1];
        const intersect = ((yi > y) != (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
        if (intersect) {
            inside = !inside;
        }
    }
    return inside;
}
exports.inside_polygon = inside_polygon;
;
function area_polygon(polygon) {
    const { coords } = polygon;
    let area = 0;
    for (let i = 0, j = coords.length - 1; i < coords.length; i++) {
        area += (coords[j][0] + coords[i][0]) * Math.abs(coords[j][1] - coords[i][1]);
        j = i;
    }
    return Math.abs(area / 2);
}
exports.area_polygon = area_polygon;
;
//# sourceMappingURL=polygons.js.map