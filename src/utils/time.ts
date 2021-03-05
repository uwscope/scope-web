import { setHours, setMilliseconds, setMinutes, setSeconds } from 'date-fns';

export const clearTime = (date: Date) => {
    return setMilliseconds(setSeconds(setMinutes(setHours(date, 0), 0), 0), 0);
};
