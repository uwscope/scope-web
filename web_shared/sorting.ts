import { compareAsc } from "date-fns";
import { toLocalDateTime } from "shared/time";
import {
  IActivity,
  IActivitySchedule,
  ICaseReview,
  ISession,
} from "shared/types";

export const compareActivityByName: (
  compareA: IActivity,
  compareB: IActivity,
) => number = function (compareA, compareB) {
  return compareStringCaseInsensitive(compareA.name, compareB.name);
};

export const compareActivityScheduleByDateAndTime: (
  compareA: IActivitySchedule,
  compareB: IActivitySchedule,
) => number = function (compareA, compareB) {
  const compareDateA = toLocalDateTime(compareA.date, compareA.timeOfDay);
  const compareDateB = toLocalDateTime(compareB.date, compareB.timeOfDay);

  return compareAsc(compareDateA, compareDateB);
};

export const compareCaseReviewsByDate: (
  compareA: ICaseReview,
  compareB: ICaseReview,
) => number = function (compareA, compareB): number {
  return compareAsc(compareA.date, compareB.date);
};

export const compareCaseReviewsOrSessionsByDate: (
  compareA: ICaseReview | ISession,
  compareB: ICaseReview | ISession,
) => number = function (compareA, compareB): number {
  return compareAsc(compareA.date, compareB.date);
};

export const compareSessionsByDate: (
  compareA: ISession,
  compareB: ISession,
) => number = function (compareA, compareB) {
  return compareAsc(compareA.date, compareB.date);
};

export const compareStringCaseInsensitive: (
  compareA: string,
  compareB: string,
) => number = function (compareA, compareB) {
  const compareInsensitiveA = compareA.toLocaleLowerCase();
  const compareInsensitiveB = compareB.toLocaleLowerCase();

  return compareInsensitiveA.localeCompare(compareInsensitiveB);
};

export const sortActivitiesByName: (activities: IActivity[]) => IActivity[] =
  function (activities) {
    return activities.slice().sort(compareActivityByName);
  };

export const sortActivitySchedulesByDateAndTime: (
  activitySchedules: IActivitySchedule[],
) => IActivitySchedule[] = function (activitySchedules) {
  return activitySchedules.slice().sort(compareActivityScheduleByDateAndTime);
};

export const sortCaseReviewsByDate: (
  caseReviews: ICaseReview[],
) => ICaseReview[] = function (caseReviews) {
  return caseReviews.slice().sort(compareCaseReviewsByDate);
};

export const sortCaseReviewsOrSessionsByDate: (
  caseReviewsOrSessions: (ICaseReview | ISession)[],
) => (ICaseReview | ISession)[] = function (caseReviewsOrSessions) {
  return caseReviewsOrSessions.slice().sort(compareCaseReviewsOrSessionsByDate);
};

export const sortSessionsByDate: (sessions: ISession[]) => ISession[] =
  function (sessions) {
    return sessions.slice().sort(compareSessionsByDate);
  };

export const sortStringsCaseInsensitive: (strings: string[]) => string[] =
  function (strings) {
    return strings.slice().sort(compareStringCaseInsensitive);
  };
