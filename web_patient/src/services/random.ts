import { random } from 'lodash';

export const getRandomItem = <T>(array: ReadonlyArray<T>) => {
    return array[random(0, array.length)];
};

export const getRandomFlags = (array: ReadonlyArray<string>) => {
    const flags: { [key: string]: boolean } = {};
    array.forEach((k) => (flags[k] = random(0, array.length) <= 1));
    return flags;
};

export const getRandomBoolean = () => {
    return random(2) <= 1;
}

export const sample = <T>(array: ReadonlyArray<T>, count: number) => {
    const shuffledIdx = [...Array(array.length).keys()]
        .map((_, idx) => [idx, Math.random()])
        .sort((a, b) => (a[1] < b[1] ? -1 : 1))
        .map((t) => t[0]);

    return shuffledIdx.filter((_, idx) => idx < count).map((idx) => array[idx]);
};
