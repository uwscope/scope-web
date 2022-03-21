import { format, parse, parseISO, setHours, setMilliseconds, setMinutes, setSeconds } from 'date-fns';
import { FollowupSchedule } from 'shared/enums';

export const clearTime = (date: Date) => {
    return setMilliseconds(setSeconds(setMinutes(setHours(date, 0), 0), 0), 0);
};

// TODO: Remove after migration is complete
const isoDateTimeFormat =
    /^([0-9]{4})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])(|.[0-9]*)$/;
const isoDateTimeFormatNew =
    /^([0-9]{4})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])(|.[0-9]*)Z$/;
const justDateFormat = /^([0-9]{4})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$/;
const dateFormat = 'yyyy-MM-dd';
const dateFieldSuffix = 'date';

const isIsoDateTimeString = (value: any): boolean => {
    return !!value && typeof value === 'string' && (isoDateTimeFormat.test(value) || isoDateTimeFormatNew.test(value));
};

const isJustDateString = (value: any): boolean => {
    return !!value && typeof value === 'string' && justDateFormat.test(value);
};

const isInstanceOfDate = (value: any): boolean => {
    return Object.prototype.toString.call(value) === '[object Date]';
};

export const handleResponseDates = (body: any) => {
    if (body === null || body === undefined || typeof body !== 'object') {
        return body;
    }

    for (const key of Object.keys(body)) {
        const value = body[key];
        if (isIsoDateTimeString(value)) {
            body[key] = parseISO(value);
        } else if (isJustDateString(value)) {
            body[key] = parse(value, dateFormat, new Date(0, 0, 0, 0, 0, 0));
        } else if (typeof value === 'object') {
            handleResponseDates(value);
        }
    }
};

export const handleRequestDates = (body: any) => {
    if (body === null || body === undefined || typeof body !== 'object') {
        return body;
    }

    for (const key of Object.keys(body)) {
        const value = body[key];
        if (isInstanceOfDate(value) && key.toLowerCase().endsWith(dateFieldSuffix)) {
            body[key] = format(value, dateFormat);
        } else if (typeof value === 'object') {
            handleRequestDates(value);
        }
    }
};

export const getFollowupWeeks = (schedule: FollowupSchedule) => {
    switch (schedule) {
        case '1-week follow-up':
            return 1;
        case '2-week follow-up':
            return 2;
        case '4-week follow-up':
            return 4;
        default:
            return 0;
    }
};
