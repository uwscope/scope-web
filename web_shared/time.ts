import { format, parseISO, setHours, setMilliseconds, setMinutes, setSeconds } from 'date-fns';
import { utcToZonedTime } from 'date-fns-tz';
import { FollowupSchedule } from 'shared/enums';

export const clearTime = (date: Date) => {
    return setMilliseconds(setSeconds(setMinutes(setHours(date, 0), 0), 0), 0);
};

// Takes the "date" type from service and converts it to a formatted date only string
export const formatDateOnly = (date: Date | number, formatter: string = 'MM/dd/yy') => {
    return format(toLocalDateOnly(date), formatter);
};

// Takes the "date" type from service and converts it to a local date only object
export const toLocalDateOnly = (date: Date | number) => {
    return utcToZonedTime(date, '+00');
};

// Takes the local date only object and converts to service's "date" type
export const toUTCDateOnly = (date: Date) => {
    // TODO: Investigate new Intl APIs for extracting current timezones
    return new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate(), 0, 0, 0));
};

// TODO: Remove after migration is complete
const isoDateFormat =
    /^([0-9]{4})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])(|.[0-9]*)$/;
const isoDateFormatNew =
    /^([0-9]{4})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])(|.[0-9]*)Z$/;

const isIsoDateString = (value: any): boolean => {
    return !!value && typeof value === 'string' && (isoDateFormat.test(value) || isoDateFormatNew.test(value));
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

export const getFollowupWeeks = (schedule: FollowupSchedule) => {
    switch (schedule) {
        case '1-week follow-up':
            return 1;
        case '2-week follow-up':
            return 2;
        case '3-week follow-up':
            return 3;
        case '4-week follow-up':
            return 4;
        case '6-week follow-up':
            return 6;
        case '8-week follow-up':
            return 8;
        default:
            return 0;
    }
};
