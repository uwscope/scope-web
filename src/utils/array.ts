export const unique = <T>(array: T[]) => {
    return array.filter((v: T, idx: number, a: T[]) => a.indexOf(v) === idx);
};

export const contains = <T>(array: T[], value: T) => {
    return array.indexOf(value) >= 0;
};
