declare type NumpyData = {
    data: {
        buffer: Iterable<number>;
    };
    shape: number[];
};
export declare type PolyStyle = {
    color?: string;
    alpha?: string;
    size?: number;
};
export declare type Coordinate = [number, number];
export declare type Polygon = PolyStyle & {
    coords: Coordinate[];
};
export declare function deserialize_numpy(data: NumpyData): {
    data: Uint8ClampedArray;
    shape: number[];
} | null;
export declare function serialize_numpy(data: NumpyData): NumpyData;
export declare function centroid_polygon(coords: Coordinate[]): Coordinate;
export declare function inside_polygon(point: Coordinate, coords: Coordinate[]): boolean;
export declare function area_polygon(coords: Coordinate[]): number;
export {};
