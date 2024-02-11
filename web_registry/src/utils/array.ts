export const unique = <T>(array: T[]) => {
  return array.filter((v: T, idx: number, a: T[]) => a.indexOf(v) === idx);
};

export const contains = <T>(array: T[], value: T) => {
  return array.indexOf(value) >= 0;
};

export const sum = (array: number[]) => {
  return array.reduce((prev, cur) => prev + cur, 0);
};

export const mean = (array: number[]) => {
  if (array.length > 0) {
    return sum(array) / array.length;
  } else {
    return undefined;
  }
};

export const last = <T>(array: T[]) => {
  if (array.length > 0) {
    return array[array.length - 1];
  } else {
    return undefined;
  }
};

export const max = (array: number[]) => {
  return array.reduce((prev, cur) => Math.max(prev, cur), 0);
};
