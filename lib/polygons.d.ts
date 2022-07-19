export declare type PolyStyle = {
    color?: string;
    alpha?: string;
    size?: number;
};
declare type Coordinate = [number, number];
export declare type Polygon = PolyStyle & {
    coords: Coordinate[];
};
export declare function centroid_polygon(polygon: Polygon): Coordinate;
export declare function inside_polygon(point: Coordinate, polygon: Polygon): boolean;
export declare function area_polygon(polygon: Polygon): number;
export {};
