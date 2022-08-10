export type PolyStyle = {
  color?: string;
  alpha?: string;
  size?: number;
};

export type Coordinate = [number, number];

export type Polygon = PolyStyle & {
  coords: Coordinate[];
  label?: string;
};

export function centroid_polygon(polygon: Polygon): Coordinate {
  const centroid: Coordinate = [0, 0];
  const { coords } = polygon;

  for (const [x, y] of coords) {
    centroid[0] += x;
    centroid[1] += y;
  }

  centroid[0] /= coords.length;
  centroid[1] /= coords.length;

  return centroid;
}

export function inside_polygon(point: Coordinate, polygon: Polygon): boolean {
  // ray-casting algorithm based on
  // https://wrf.ecse.rpi.edu/Research/Short_Notes/pnpoly.html/pnpoly.html
  const x = point[0],
    y = point[1];
  const { coords } = polygon;

  let inside = false;
  for (let i = 0, j = coords.length - 1; i < coords.length; j = i++) {
    const xi = coords[i][0],
      yi = coords[i][1];
    const xj = coords[j][0],
      yj = coords[j][1];
    const intersect = yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi;

    if (intersect) {
      inside = !inside;
    }
  }

  return inside;
}

export function area_polygon(polygon: Polygon): number {
  const { coords } = polygon;
  let area = 0;

  for (let i = 0, j = coords.length - 1; i < coords.length; i++) {
    area += coords[j][0] * coords[i][1] - coords[j][1] * coords[i][0];
    j = i;
  }

  return Math.abs(area / 2);
}
