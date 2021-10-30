export const getRandomInteger = (minInclusive: number, maxExclusive: number) => {
    return Math.floor(Math.random() * (maxExclusive - minInclusive) + minInclusive);
};

export const getRandomItem = <T>(array: ReadonlyArray<T>) => {
    return array[getRandomInteger(0, array.length)];
};

export const getRandomFlags = (array: ReadonlyArray<string>) => {
    const flags: { [key: string]: boolean } = {};
    array.forEach((k) => (flags[k] = getRandomInteger(0, array.length) <= 1));
    return flags;
};

export const sample = <T>(array: ReadonlyArray<T>, count: number) => {
    const shuffledIdx = [...Array(array.length).keys()]
        .map((_, idx) => [idx, Math.random()])
        .sort((a, b) => (a[1] < b[1] ? -1 : 1))
        .map((t) => t[0]);

    return shuffledIdx.filter((_, idx) => idx < count).map((idx) => array[idx]);
};

export const getRandomBoolean = () => {
    return Math.random() >= 0.5;
};
