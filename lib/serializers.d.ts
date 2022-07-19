declare type NumpyData = {
    data: {
        buffer: Iterable<number>;
    };
    shape: number[];
};
export declare function deserialize_numpy(data: NumpyData): {
    data: Uint8ClampedArray;
    shape: number[];
} | null;
export declare function serialize_numpy(data: NumpyData): NumpyData;
export {};
