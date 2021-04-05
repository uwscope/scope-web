import { parseISO, setHours, setMilliseconds, setMinutes, setSeconds } from 'date-fns';

export const clearTime = (date: Date) => {
    return setMilliseconds(setSeconds(setMinutes(setHours(date, 0), 0), 0), 0);
};

const isoDateFormat = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d*)?$/;

const isIsoDateString = (value: any): boolean => {
    return !!value && typeof value === 'string' && isoDateFormat.test(value);
};

export const handleDates = (body: any) => {
    if (body === null || body === undefined || typeof body !== 'object') {
        return body;
    }

    for (const key of Object.keys(body)) {
        const value = body[key];
        if (isIsoDateString(value)) {
            body[key] = parseISO(value);
        } else if (typeof value === 'object') {
            handleDates(value);
        }
    }
};
