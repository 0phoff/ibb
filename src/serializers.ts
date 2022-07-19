type NumpyData = {
  data: { buffer: Iterable<number> };
  shape: number[];
};

export function deserialize_numpy(data: NumpyData) {
  if (data === null) {
    return null;
  }

  return {
    data: new Uint8ClampedArray(data.data.buffer),
    shape: data.shape,
  };
}

export function serialize_numpy(data: NumpyData) {
  return data;
}
