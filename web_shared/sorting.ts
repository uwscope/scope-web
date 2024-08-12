import { compareAsc } from "date-fns";
import { toLocalDateTime } from "shared/time";
import {
  IActivity,
  IActivityLog,
  IActivitySchedule,
  IAssessmentLog,
  ICaseReview,
  IMoodLog,
  IReviewMark,
  IScheduledActivity,
  ISession,
  IValue,
} from "shared/types";

export const enum SortDirection {
  ASCENDING,
  DESCENDING,
}

export const sortingDirectionComparator: <T>(
  comparator: (compareA: T, compareB: T) => number,
  sortingDirection: SortDirection,
) => (compareA: T, compareB: T) => number = function (
  comparator,
  sortingDirection,
) {
  switch (sortingDirection) {
    case SortDirection.ASCENDING:
      return comparator;
    case SortDirection.DESCENDING:
      return (compareA, compareB) => comparator(compareB, compareA);
  }
};

export const compareActivityByName: (
  compareA: IActivity,
  compareB: IActivity,
) => number = function (compareA, compareB) {
  return compareStringCaseInsensitive(compareA.name, compareB.name);
};

export const compareActivitiesByDateAndTime: (
  compareA: IActivity,
  compareB: IActivity,
) => number = function (compareA, compareB): number {
  return compareAsc(compareA.editedDateTime, compareB.editedDateTime);
};

export const compareActivityLogsByDateAndTime: (
  compareA: IActivityLog,
  compareB: IActivityLog,
) => number = function (compareA, compareB): number {
  return compareAsc(compareA.recordedDateTime, compareB.recordedDateTime);
};

export const compareActivityScheduleByDateAndTime: (
  compareA: IActivitySchedule,
  compareB: IActivitySchedule,
) => number = function (compareA, compareB) {
  const compareDateA = toLocalDateTime(compareA.date, compareA.timeOfDay);
  const compareDateB = toLocalDateTime(compareB.date, compareB.timeOfDay);

  return compareAsc(compareDateA, compareDateB);
};

export const compareAssessmentLogsByDateAndTime: (
  compareA: IAssessmentLog,
  compareB: IAssessmentLog,
) => number = function (compareA, compareB): number {
  return compareAsc(compareA.recordedDateTime, compareB.recordedDateTime);
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

export const compareMoodLogsByDateAndTime: (
  compareA: IMoodLog,
  compareB: IMoodLog,
) => number = function (compareA, compareB): number {
  return compareAsc(compareA.recordedDateTime, compareB.recordedDateTime);
};

export const compareReviewMarksByEditedDateAndTime: (
  compareA: IReviewMark,
  compareB: IReviewMark,
) => number = function (compareA, compareB): number {
  return compareAsc(compareA.editedDateTime, compareB.editedDateTime);
};

export const compareScheduledActivitiesByDateAndTime: (
  compareA: IScheduledActivity,
  compareB: IScheduledActivity,
) => number = function (compareA, compareB): number {
  return compareAsc(compareA.dueDateTime, compareB.dueDateTime);
};

export const compareSessionsByDate: (
  compareA: ISession,
  compareB: ISession,
) => number = function (compareA, compareB) {
  return compareAsc(compareA.date, compareB.date);
};

export const compareValuesByDateAndTime: (
  compareA: IValue,
  compareB: IValue,
) => number = function (compareA, compareB): number {
  return compareAsc(compareA.editedDateTime, compareB.editedDateTime);
};

export const compareStringCaseInsensitive: (
  compareA: string,
  compareB: string,
) => number = function (compareA, compareB) {
  const compareInsensitiveA = compareA.toLocaleLowerCase();
  const compareInsensitiveB = compareB.toLocaleLowerCase();

  return compareInsensitiveA.localeCompare(compareInsensitiveB);
};

export const sortActivitiesByDateAndTime: (
  activities: IActivity[],
  sortingDirection?: SortDirection,
) => IActivity[] = function (
  activities,
  sortingDirection = SortDirection.ASCENDING,
) {
  return activities
    .slice()
    .sort(
      sortingDirectionComparator(
        compareActivitiesByDateAndTime,
        sortingDirection,
      ),
    );
};

export const sortActivitiesByName: (activities: IActivity[]) => IActivity[] =
  function (activities) {
    return activities.slice().sort(compareActivityByName);
  };

export const sortActivityLogsByDateAndTime: (
  activityLogs: IActivityLog[],
  sortingDirection?: SortDirection,
) => IActivityLog[] = function (
  activityLogs,
  sortingDirection = SortDirection.ASCENDING,
) {
  return activityLogs
    .slice()
    .sort(
      sortingDirectionComparator(
        compareActivityLogsByDateAndTime,
        sortingDirection,
      ),
    );
};

export const sortActivitySchedulesByDateAndTime: (
  activitySchedules: IActivitySchedule[],
) => IActivitySchedule[] = function (activitySchedules) {
  return activitySchedules.slice().sort(compareActivityScheduleByDateAndTime);
};

export const sortAssessmentLogsByDateAndTime: (
  assessmentLogs: IAssessmentLog[],
  sortingDirection?: SortDirection,
) => IAssessmentLog[] = function (
  assessmentLogs,
  sortingDirection = SortDirection.ASCENDING,
) {
  return assessmentLogs
    .slice()
    .sort(
      sortingDirectionComparator(
        compareAssessmentLogsByDateAndTime,
        sortingDirection,
      ),
    );
};

export const sortCaseReviewsByDate: (
  caseReviews: ICaseReview[],
) => ICaseReview[] = function (caseReviews) {
  return caseReviews.slice().sort(compareCaseReviewsByDate);
};

export const sortCaseReviewsOrSessionsByDate: (
  caseReviewsOrSessions: (ICaseReview | ISession)[],
  sortingDirection?: SortDirection,
) => (ICaseReview | ISession)[] = function (
  caseReviewsOrSessions,
  sortingDirection = SortDirection.ASCENDING,
) {
  return caseReviewsOrSessions
    .slice()
    .sort(
      sortingDirectionComparator(
        compareCaseReviewsOrSessionsByDate,
        sortingDirection,
      ),
    );
};

export const sortMoodLogsByDateAndTime: (
  moodLogs: IMoodLog[],
  sortingDirection?: SortDirection,
) => IMoodLog[] = function (
  moodLogs,
  sortingDirection = SortDirection.ASCENDING,
) {
  return moodLogs
    .slice()
    .sort(
      sortingDirectionComparator(
        compareMoodLogsByDateAndTime,
        sortingDirection,
      ),
    );
};

export const sortReviewMarksByEditedDateAndTime: (
  reviewMarks: IReviewMark[],
  sortingDirection?: SortDirection,
) => IReviewMark[] = function (
  reviewMarks,
  sortingDirection = SortDirection.ASCENDING,
) {
  return reviewMarks
    .slice()
    .sort(
      sortingDirectionComparator(
        compareReviewMarksByEditedDateAndTime,
        sortingDirection,
      ),
    );
};

export const sortScheduledActivitiesByDateAndTime: (
  scheduledActivities: IScheduledActivity[],
  sortingDirection?: SortDirection,
) => IScheduledActivity[] = function (
  scheduledActivities,
  sortingDirection = SortDirection.ASCENDING,
) {
  return scheduledActivities
    .slice()
    .sort(
      sortingDirectionComparator(
        compareScheduledActivitiesByDateAndTime,
        sortingDirection,
      ),
    );
};

export const sortSessionsByDate: (sessions: ISession[]) => ISession[] =
  function (sessions) {
    return sessions.slice().sort(compareSessionsByDate);
  };

export const sortValuesByDateAndTime: (
  values: IValue[],
  sortingDirection?: SortDirection,
) => IValue[] = function (values, sortingDirection = SortDirection.ASCENDING) {
  return values
    .slice()
    .sort(
      sortingDirectionComparator(compareValuesByDateAndTime, sortingDirection),
    );
};

export const sortStringsCaseInsensitive: (strings: string[]) => string[] =
  function (strings) {
    return strings.slice().sort(compareStringCaseInsensitive);
  };
