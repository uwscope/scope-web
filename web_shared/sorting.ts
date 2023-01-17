import { compareAsc } from 'date-fns';

import { toLocalDateTime } from "shared/time";
import { IActivity, IActivitySchedule } from 'shared/types';

export const compareActivityByName: (
    compareA: IActivity,
    compareB: IActivity,
) => number = function (
    compareA: IActivity,
    compareB: IActivity,
): number {
    const compareNameA = compareA.name.toLocaleLowerCase();
    const compareNameB = compareB.name.toLocaleLowerCase();

    return compareNameA.localeCompare(compareNameB);
};

export const compareActivityScheduleByDateAndTime: (
    compareA: IActivitySchedule,
    compareB: IActivitySchedule,
) => number = function (
    compareA: IActivitySchedule,
    compareB: IActivitySchedule,
): number {
    const compareDateA = toLocalDateTime(compareA.date, compareA.timeOfDay);
    const compareDateB = toLocalDateTime(compareB.date, compareB.timeOfDay);

    return compareAsc(compareDateA, compareDateB);
};

export const sortActivitiesByName: (
    activities: IActivity[],
) => IActivity[] = function(
    activities: IActivity[],
): IActivity[] {
    return activities.slice().sort(
        compareActivityByName
    )
};

export const sortActivitySchedulesByDateAndTime: (
    activitySchedules: IActivitySchedule[]
) => IActivitySchedule[] = function (
    activitySchedules: IActivitySchedule[]
): IActivitySchedule[] {
    return activitySchedules.slice().sort(
        compareActivityScheduleByDateAndTime
    )
};
