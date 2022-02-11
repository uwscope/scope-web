import { parseISO, setHours, setMilliseconds, setMinutes, setSeconds } from 'date-fns';
import { FollowupSchedule } from 'shared/enums';

export const clearTime = (date: Date) => {
    return setMilliseconds(setSeconds(setMinutes(setHours(date, 0), 0), 0), 0);
};

// TODO: Remove after migration is complete
const isoDateFormat = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d*)?$/;
const isoDateFormatNew = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d*)?Z$/;

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
        case '4-week follow-up':
            return 4;
        default:
            return 0;
    }
};
