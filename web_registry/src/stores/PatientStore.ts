import { differenceInYears, max, subDays } from "date-fns";
import { action, computed, makeAutoObservable, toJS } from "mobx";
import {
  behavioralActivationChecklistValues,
  behavioralStrategyChecklistValues,
  cancerTreatmentRegimenValues,
  discussionFlagValues,
  patientRaceValues,
} from "shared/enums";
import { getLogger } from "shared/logger";
import {
  getPatientServiceInstance,
  IPatientService,
} from "shared/patientService";
import { IPromiseQueryState, PromiseQuery } from "shared/promiseQuery";
import {
  sortActivitiesByDateAndTime,
  sortActivityLogsByDateAndTime,
  sortAssessmentLogsByDateAndTime,
  sortCaseReviewsByDate,
  sortCaseReviewsOrSessionsByDate,
  SortDirection,
  sortMoodLogsByDateAndTime,
  sortReviewMarksByEditedDateAndTime,
  sortScheduledActivitiesByDateAndTime,
  sortSessionsByDate,
  sortValuesByDateAndTime,
} from "shared/sorting";
import {
  getLoadAndLogQuery,
  onArrayConflict,
  onSingletonConflict,
} from "shared/stores";
import { toLocalDateOnly } from "shared/time";
import {
  IActivity,
  IActivityLog,
  IActivitySchedule,
  IAssessment,
  IAssessmentLog,
  ICaseReview,
  IClinicalHistory,
  IMoodLog,
  IPatient,
  IPatientProfile,
  IReviewMark,
  ISafetyPlan,
  IScheduledActivity,
  IScheduledAssessment,
  ISession,
  IValue,
  IValuesInventory,
} from "shared/types";

const logger = getLogger("PatientStore");

export interface IPatientStore extends IPatient {
  readonly age: number;
  readonly name: string;
  readonly latestCaseReview: ICaseReview | undefined;
  readonly latestSession: ISession | undefined;
  readonly recordId: string;

  // Recent patient entry properties
  readonly recentEntryCaseloadSummary: string | undefined;
  readonly recentEntryCutoffDateTime: Date;
  readonly recentEntryActivities: IActivity[] | undefined;
  readonly recentEntryActivityLogsSortedByDateAndTimeDescending:
    | IActivityLog[]
    | undefined;
  readonly recentEntryAssessmentLogsSortedByDateAndTimeDescending:
    | IAssessmentLog[]
    | undefined;
  readonly recentEntryMoodLogsSortedByDateAndTimeDescending:
    | IMoodLog[]
    | undefined;
  readonly recentEntrySafetyPlan: ISafetyPlan | undefined;
  readonly recentEntryScheduledActivitiesSortedByDateAndTimeDescending:
    | IScheduledActivity[]
    | undefined;
  readonly recentEntryValues: IValue[] | undefined;

  // UI states
  readonly loadPatientState: IPromiseQueryState;

  readonly loadActivitiesState: IPromiseQueryState;
  readonly loadActivityLogsState: IPromiseQueryState;
  readonly loadActivitySchedulesState: IPromiseQueryState;
  readonly loadAssessmentsState: IPromiseQueryState;
  readonly loadAssessmentLogsState: IPromiseQueryState;
  readonly loadCaseReviewsState: IPromiseQueryState;
  readonly loadClinicalHistoryState: IPromiseQueryState;
  readonly loadMoodLogsState: IPromiseQueryState;
  readonly loadProfileState: IPromiseQueryState;
  readonly loadReviewMarksState: IPromiseQueryState;
  readonly loadSafetyPlanState: IPromiseQueryState;
  readonly loadScheduledActivitiesState: IPromiseQueryState;
  readonly loadScheduledAssessmentsState: IPromiseQueryState;
  readonly loadSessionsState: IPromiseQueryState;
  readonly loadValuesState: IPromiseQueryState;
  readonly loadValuesInventoryState: IPromiseQueryState;

  // Sorted properties
  readonly activitiesSortedByDateAndTimeDescending: IActivity[];
  readonly activityLogsSortedByDateAndTimeDescending: IActivityLog[];
  readonly assessmentLogsSortedByDateAndTime: IAssessmentLog[];
  readonly assessmentLogsSortedByDateAndTimeDescending: IAssessmentLog[];
  readonly caseReviewsSortedByDate: ICaseReview[];
  readonly caseReviewsOrSessionsSortedByDate: (ICaseReview | ISession)[];
  readonly caseReviewsOrSessionsSortedByDateDescending: (
    | ICaseReview
    | ISession
  )[];
  readonly sessionsSortedByDate: ISession[];
  readonly moodLogsSortedByDateAndTime: IMoodLog[];
  readonly moodLogsSortedByDateAndTimeDescending: IMoodLog[];
  readonly reviewMarksSortedByEditedDateAndTimeDescending: IReviewMark[];
  readonly scheduledActivitiesSortedByDateAndTimeDescending: IScheduledActivity[];
  readonly valuesSortedByDateAndTimeDescending: IValue[];

  // Filters
  readonly valuesWithoutActivity: IValue[];

  // Helpers
  getActivitiesByLifeAreaId: (lifeAreaId: string) => IActivity[];
  getActivitiesByValueId: (valueId: string) => IActivity[];
  getActivityById: (activityId: string) => IActivity | undefined;
  getAssessmentLogById: (assessmentLogId: string) => IAssessmentLog | undefined;
  getCaseReviewById: (caseReviewId: string) => ICaseReview | undefined;
  getMoodLogById: (moodLogId: string) => IMoodLog | undefined;
  getRecentEntryActivityById: (activityId: string) => IActivity | undefined;
  getRecentEntryAssessmentLogById: (
    assessmentLogId: string,
  ) => IAssessmentLog | undefined;
  getRecentEntryValueById: (valueId: string) => IValue | undefined;
  getRecentEntryAssessmentLogsSortedByDateAndTimeDescendingByAssessmentId: (
    assessmentId: string,
  ) => IAssessmentLog[] | undefined;
  getRecentEntryMoodLogById: (moodLogId: string) => IMoodLog | undefined;
  getRecentEntryScheduledActivityById: (
    scheduledActivityId: string,
  ) => IScheduledActivity | undefined;
  getScheduledActivityById: (
    scheduledActivityId: string,
  ) => IScheduledActivity | undefined;
  getSessionById: (sessionId: string) => ISession | undefined;
  getValueById: (valueId: string) => IValue | undefined;

  // Data load/save
  load(getToken?: () => string | undefined, onUnauthorized?: () => void): void;

  // Assessments
  addAssessmentLog(assessmentLog: IAssessmentLog): void;
  updateAssessment(assessment: IAssessment): void;
  updateAssessmentLog(assessmentLog: IAssessmentLog): void;

  // Assignments
  assignAssessment(assessmentId: string): void;
  cancelAssessment(assessmentId: string): void;
  assignSafetyPlan(): void;
  assignValuesInventory(): void;

  // Case Review
  addCaseReview(caseReview: ICaseReview): void;
  updateCaseReview(caseReview: ICaseReview): void;

  // Clinical History
  updateClinicalHistory(history: IClinicalHistory): Promise<void>;

  // Patient profile
  updateProfile(profile: IPatientProfile): Promise<void>;

  // Review marks that define recent entry data
  addReviewMark(review: IReviewMark): Promise<void>;

  // Session
  addSession(session: ISession): void;
  updateSession(session: ISession): void;
}

export class PatientStore implements IPatientStore {
  private readonly loadPatientDataQuery: PromiseQuery<IPatient>;
  private readonly loadActivitiesQuery: PromiseQuery<IActivity[]>;
  private readonly loadActivityLogsQuery: PromiseQuery<IActivityLog[]>;
  private readonly loadActivitySchedulesQuery: PromiseQuery<
    IActivitySchedule[]
  >;
  private readonly loadAssessmentsQuery: PromiseQuery<IAssessment[]>;
  private readonly loadAssessmentLogsQuery: PromiseQuery<IAssessmentLog[]>;
  private readonly loadCaseReviewsQuery: PromiseQuery<ICaseReview[]>;
  private readonly loadClinicalHistoryQuery: PromiseQuery<IClinicalHistory>;
  private readonly loadMoodLogsQuery: PromiseQuery<IMoodLog[]>;
  private readonly loadProfileQuery: PromiseQuery<IPatientProfile>;
  private readonly loadReviewMarksQuery: PromiseQuery<IReviewMark[]>;
  private readonly loadSafetyPlanQuery: PromiseQuery<ISafetyPlan>;
  private readonly loadSessionsQuery: PromiseQuery<ISession[]>;
  private readonly loadScheduledActivitiesQuery: PromiseQuery<
    IScheduledActivity[]
  >;
  private readonly loadScheduledAssessmentsQuery: PromiseQuery<
    IScheduledAssessment[]
  >;
  private readonly loadValuesQuery: PromiseQuery<IValue[]>;
  private readonly loadValuesInventoryQuery: PromiseQuery<IValuesInventory>;

  private readonly patientService: IPatientService;

  private loadAndLogQuery: <T>(
    queryCall: () => Promise<T>,
    promiseQuery: PromiseQuery<T>,
    onConflict?: (responseData?: any) => T,
  ) => Promise<void>;

  constructor(patient: IPatient) {
    console.assert(
      !!patient.identity,
      "Attempted to create a patient object without identity",
    );
    console.assert(
      !!patient.identity.name,
      "Attempted to create a patient object without a name",
    );
    console.assert(
      !!patient.identity.patientId,
      "Attempted to create a patient object without an id",
    );

    this.patientService = getPatientServiceInstance(
      CLIENT_CONFIG.flaskBaseUrl,
      patient.identity.patientId,
    );

    this.loadAndLogQuery = getLoadAndLogQuery(logger, this.patientService);

    this.loadPatientDataQuery = new PromiseQuery<IPatient>(
      patient,
      "loadPatientData",
    );

    this.loadActivitiesQuery = new PromiseQuery<IActivity[]>(
      patient.activities,
      "loadActivities",
    );
    this.loadActivityLogsQuery = new PromiseQuery<IActivityLog[]>(
      patient.activityLogs,
      "loadActivityLogs",
    );
    this.loadActivitySchedulesQuery = new PromiseQuery<IActivitySchedule[]>(
      [],
      "loadActivitySchedulesQuery",
    );
    this.loadAssessmentsQuery = new PromiseQuery<IAssessment[]>(
      patient.assessments,
      "loadAssessments",
    );
    this.loadAssessmentLogsQuery = new PromiseQuery<IAssessmentLog[]>(
      patient.assessmentLogs,
      "loadAssessmentLogs",
    );

    this.loadCaseReviewsQuery = new PromiseQuery<ICaseReview[]>(
      patient.caseReviews,
      "loadCaseReviews",
    );
    this.loadClinicalHistoryQuery = new PromiseQuery<IClinicalHistory>(
      patient.clinicalHistory,
      "loadClinicalHistory",
    );
    this.loadMoodLogsQuery = new PromiseQuery<IMoodLog[]>(
      patient.moodLogs,
      "loadMoodLogs",
    );
    this.loadProfileQuery = new PromiseQuery<IPatientProfile>(
      patient.profile,
      "loadProfile",
    );
    this.loadReviewMarksQuery = new PromiseQuery<IReviewMark[]>(
      patient.reviewMarks,
      "loadReviewMarks",
    );
    this.loadSafetyPlanQuery = new PromiseQuery<ISafetyPlan>(
      patient.safetyPlan,
      "loadSafetyPlan",
    );
    this.loadScheduledActivitiesQuery = new PromiseQuery<IScheduledActivity[]>(
      patient.scheduledActivities,
      "loadScheduledActivities",
    );
    this.loadScheduledAssessmentsQuery = new PromiseQuery<
      IScheduledAssessment[]
    >(patient.scheduledAssessments, "loadScheduledAssessments");
    this.loadSessionsQuery = new PromiseQuery<ISession[]>(
      patient.sessions,
      "loadSessions",
    );
    this.loadValuesQuery = new PromiseQuery<IValue[]>([], "loadValuesQuery");
    this.loadValuesInventoryQuery = new PromiseQuery<IValuesInventory>(
      patient.valuesInventory,
      "loadValuesInventory",
    );

    makeAutoObservable(this);
  }

  @computed get activities() {
    return this.loadActivitiesQuery.value || [];
  }

  @computed get activityLogs() {
    return this.loadActivityLogsQuery.value || [];
  }

  @computed get activitiesSortedByDateAndTimeDescending() {
    return sortActivitiesByDateAndTime(
      this.activities,
      SortDirection.DESCENDING,
    );
  }

  @computed get activityLogsSortedByDateAndTimeDescending() {
    return sortActivityLogsByDateAndTime(
      this.activityLogs,
      SortDirection.DESCENDING,
    );
  }

  @computed get activitySchedules(): IActivitySchedule[] {
    return this.loadActivitySchedulesQuery.value || [];

    // TODO Activity Refactor: I don't think this is necessary?
    // return (this.loadActivitySchedulesQuery.value || [])
    //     .map(
    //         (as) =>
    //             ({
    //                 ...as,
    //                 repeatDayFlags: Object.assign(
    //                     {},
    //                     ...daysOfWeekValues.map((x) => ({
    //                         [x]: !!as?.repeatDayFlags?.[x],
    //                     })),
    //                 ),
    //             }),
    //     );
  }

  @computed get age() {
    return !!this.profile.birthdate
      ? differenceInYears(new Date(), this.profile.birthdate)
      : -1;
  }

  @computed get assessments() {
    return this.loadAssessmentsQuery.value || [];
  }

  @computed get assessmentLogs() {
    return this.loadAssessmentLogsQuery.value || [];
  }

  @computed get assessmentLogsSortedByDateAndTime() {
    return sortAssessmentLogsByDateAndTime(this.assessmentLogs);
  }

  @computed get assessmentLogsSortedByDateAndTimeDescending() {
    return sortAssessmentLogsByDateAndTime(
      this.assessmentLogs,
      SortDirection.DESCENDING,
    );
  }

  @computed get identity() {
    return (
      this.loadPatientDataQuery.value?.identity || {
        name: "Unknown",
        patientId: "Unknown",
      }
    );
  }

  @computed get moodLogs() {
    return this.loadMoodLogsQuery.value || [];
  }

  @computed get moodLogsSortedByDateAndTime() {
    return sortMoodLogsByDateAndTime(this.moodLogs);
  }

  @computed get moodLogsSortedByDateAndTimeDescending() {
    return sortMoodLogsByDateAndTime(this.moodLogs, SortDirection.DESCENDING);
  }

  @computed get reviewMarks() {
    return this.loadReviewMarksQuery.value || [];
  }

  @computed get reviewMarksSortedByEditedDateAndTimeDescending() {
    return sortReviewMarksByEditedDateAndTime(
      this.reviewMarks,
      SortDirection.DESCENDING,
    );
  }

  @computed get scheduledActivitiesSortedByDateAndTimeDescending() {
    return sortScheduledActivitiesByDateAndTime(
      this.scheduledActivities,
      SortDirection.DESCENDING,
    );
  }

  @computed get valuesSortedByDateAndTimeDescending() {
    return sortValuesByDateAndTime(this.values, SortDirection.DESCENDING);
  }

  @computed get name() {
    return this.profile.name || this.identity.name;
  }

  @computed get caseReviews() {
    return this.loadCaseReviewsQuery.value || [];
  }

  @computed get caseReviewsSortedByDate() {
    return sortCaseReviewsByDate(this.caseReviews);
  }

  @computed get caseReviewsOrSessionsSortedByDate() {
    const caseReviewsOrSessions = (
      this.caseReviews.slice() as (ICaseReview | ISession)[]
    ).concat(this.sessions);

    return sortCaseReviewsOrSessionsByDate(caseReviewsOrSessions);
  }

  @computed get caseReviewsOrSessionsSortedByDateDescending() {
    const caseReviewsOrSessions = (
      this.caseReviews.slice() as (ICaseReview | ISession)[]
    ).concat(this.sessions);

    return sortCaseReviewsOrSessionsByDate(
      caseReviewsOrSessions,
      SortDirection.DESCENDING,
    );
  }

  @computed get clinicalHistory() {
    return this.loadClinicalHistoryQuery.value || {};
  }

  @computed get latestCaseReview() {
    if (this.caseReviewsSortedByDate.length > 0) {
      return this.caseReviewsSortedByDate[
        this.caseReviewsSortedByDate.length - 1
      ];
    }

    return undefined;
  }

  @computed get latestSession() {
    if (this.sessionsSortedByDate.length > 0) {
      return this.sessionsSortedByDate[this.sessionsSortedByDate.length - 1];
    }

    return undefined;
  }

  @computed get profile() {
    return (
      this.loadProfileQuery.value || {
        name: "",
        MRN: "",
      }
    );
  }

  @computed get recentEntryCaseloadSummary() {
    const recentEntry: boolean =
      (!!this.recentEntryActivities && this.recentEntryActivities.length > 0) ||
      (!!this.recentEntryActivityLogsSortedByDateAndTimeDescending &&
        this.recentEntryActivityLogsSortedByDateAndTimeDescending.length > 0) ||
      (!!this.recentEntryAssessmentLogsSortedByDateAndTimeDescending &&
        this.recentEntryAssessmentLogsSortedByDateAndTimeDescending.length >
          0) ||
      (!!this.recentEntryMoodLogsSortedByDateAndTimeDescending &&
        this.recentEntryMoodLogsSortedByDateAndTimeDescending.length > 0) ||
      !!this.recentEntrySafetyPlan ||
      (!!this.recentEntryValues && this.recentEntryValues.length > 0);

    //
    // These currently do not render, so should not be included in determining "New"
    //
    // (!!this.recentEntryScheduledActivitiesSortedByDateAndTimeDescending &&
    //   this.recentEntryScheduledActivitiesSortedByDateAndTimeDescending.length > 0) ||

    return recentEntry ? "New" : undefined;
  }

  @computed get recentEntryCutoffDateTime() {
    // Any current mark.
    const reviewMarkCurrent =
      this.reviewMarksSortedByEditedDateAndTimeDescending.length > 0
        ? this.reviewMarksSortedByEditedDateAndTimeDescending[0]
        : undefined;

    // The effectiveDateTime of any current mark.
    const reviewMarkEffectiveCutoffDateTime =
      !!reviewMarkCurrent && !!reviewMarkCurrent.effectiveDateTime
        ? reviewMarkCurrent.effectiveDateTime
        : undefined;

    // A dateTime calculated from the stored enrollmentDate.
    const enrollmentDateCutoffDateTime = !!this.profile.enrollmentDate
      ? toLocalDateOnly(this.profile.enrollmentDate)
      : undefined;

    // A default cutoff of 2 weeks before now.
    // This is already in local time.
    const twoWeeksCutoffDateTime = subDays(new Date(), 14);

    // If there is a mark that defines an effectiveDateTime, that is the cutoff.
    if (!!reviewMarkEffectiveCutoffDateTime) {
      return reviewMarkEffectiveCutoffDateTime;
    }

    // If there is a mark, but it does not define effectiveDateTime, a person has explicitly reverted.
    // They want to see "more", so we will go as far back as we are able.
    // If there is an enrollment date, use that.
    // If there is not an enrollment date, use the "2 weeks" default.
    if (!!reviewMarkCurrent) {
      if (!!enrollmentDateCutoffDateTime) {
        return enrollmentDateCutoffDateTime;
      } else {
        return twoWeeksCutoffDateTime;
      }
    }

    // If there is no mark, we are guessing at some default.
    // Prior to the deployment of marks, that default was "2 weeks".
    // We do not want to suddenly show all data as "new" just because there is no mark.
    // So if there is no mark, continue to use the "2 weeks" default.
    // But if there is an enrollment date which is less than 2 weeks in the past, that is the effective cutoff.
    if (!!enrollmentDateCutoffDateTime) {
      return max([enrollmentDateCutoffDateTime, twoWeeksCutoffDateTime]);
    } else {
      return twoWeeksCutoffDateTime;
    }
  }

  @computed get recentEntryActivities() {
    const recentEntryCutoffDateTime = this.recentEntryCutoffDateTime;

    if (this.activities.length === 0 || !recentEntryCutoffDateTime) {
      return undefined;
    }

    const filteredActivities = this.activities.filter(
      (a) => a.editedDateTime >= recentEntryCutoffDateTime,
    );

    if (filteredActivities.length === 0) {
      return undefined;
    } else {
      return filteredActivities;
    }
  }

  @computed get recentEntryActivityLogsSortedByDateAndTimeDescending() {
    const recentEntryCutoffDateTime = this.recentEntryCutoffDateTime;

    if (
      this.activityLogsSortedByDateAndTimeDescending.length === 0 ||
      !recentEntryCutoffDateTime
    ) {
      return undefined;
    }

    const indexEnd = this.activityLogsSortedByDateAndTimeDescending.findIndex(
      (a) => a.recordedDateTime < recentEntryCutoffDateTime,
    );

    if (indexEnd < 0) {
      return this.activityLogsSortedByDateAndTimeDescending.slice();
    } else if (indexEnd === 0) {
      return undefined;
    } else {
      return this.activityLogsSortedByDateAndTimeDescending.slice(0, indexEnd);
    }
  }

  @computed get recentEntryAssessmentLogsSortedByDateAndTimeDescending() {
    const recentEntryCutoffDateTime = this.recentEntryCutoffDateTime;

    if (
      this.assessmentLogsSortedByDateAndTimeDescending.length === 0 ||
      !recentEntryCutoffDateTime
    ) {
      return undefined;
    }

    // Assessments submitted by a provider are not considered recent
    const filteredAssessmentLogs =
      this.assessmentLogsSortedByDateAndTimeDescending.filter(
        (current) => !current.submittedByProviderId,
      );

    const indexEnd = filteredAssessmentLogs.findIndex(
      (a) => a.recordedDateTime < recentEntryCutoffDateTime,
    );

    if (indexEnd < 0) {
      // No need to make a copy, it's already a copy.
      return filteredAssessmentLogs;
    } else if (indexEnd === 0) {
      return undefined;
    } else {
      return filteredAssessmentLogs.slice(0, indexEnd);
    }
  }

  @computed get recentEntryMoodLogsSortedByDateAndTimeDescending() {
    const recentEntryCutoffDateTime = this.recentEntryCutoffDateTime;

    if (
      this.moodLogsSortedByDateAndTimeDescending.length === 0 ||
      !recentEntryCutoffDateTime
    ) {
      return undefined;
    }

    const indexEnd = this.moodLogsSortedByDateAndTimeDescending.findIndex(
      (a) => a.recordedDateTime < recentEntryCutoffDateTime,
    );

    if (indexEnd < 0) {
      return this.moodLogsSortedByDateAndTimeDescending.slice();
    } else if (indexEnd === 0) {
      return undefined;
    } else {
      return this.moodLogsSortedByDateAndTimeDescending.slice(0, indexEnd);
    }
  }

  @computed get recentEntrySafetyPlan() {
    const recentEntryCutoffDateTime = this.recentEntryCutoffDateTime;

    if (!recentEntryCutoffDateTime) {
      return undefined;
    }

    // The default empty safety plan will not have a lastUpdatedDateTime
    if (
      !!this.safetyPlan.lastUpdatedDateTime &&
      this.safetyPlan.lastUpdatedDateTime >= recentEntryCutoffDateTime
    ) {
      return this.safetyPlan;
    }
    return undefined;
  }

  @computed get recentEntryScheduledActivitiesSortedByDateAndTimeDescending() {
    const recentEntryCutoffDateTime = this.recentEntryCutoffDateTime;

    if (
      this.scheduledActivitiesSortedByDateAndTimeDescending.length === 0 ||
      !recentEntryCutoffDateTime
    ) {
      return undefined;
    }

    const indexEnd =
      this.scheduledActivitiesSortedByDateAndTimeDescending.findIndex(
        (a) => a.dueDateTime < recentEntryCutoffDateTime,
      );

    if (indexEnd < 0) {
      return this.scheduledActivitiesSortedByDateAndTimeDescending.slice();
    } else if (indexEnd === 0) {
      return undefined;
    } else {
      return this.scheduledActivitiesSortedByDateAndTimeDescending.slice(
        0,
        indexEnd,
      );
    }
  }

  @computed get recentEntryValues() {
    const recentEntryCutoffDateTime = this.recentEntryCutoffDateTime;

    if (this.values.length === 0 || !recentEntryCutoffDateTime) {
      return undefined;
    }

    const filteredValues = this.values.filter(
      (a) => a.editedDateTime >= recentEntryCutoffDateTime,
    );

    if (filteredValues.length === 0) {
      return undefined;
    } else {
      return filteredValues;
    }
  }

  @computed get recordId() {
    return this.identity.patientId;
  }

  @computed get safetyPlan() {
    return this.loadSafetyPlanQuery.value || { assigned: false };
  }

  @computed get scheduledActivities() {
    return this.loadScheduledActivitiesQuery.value || [];
  }

  @computed get scheduledAssessments() {
    return this.loadScheduledAssessmentsQuery.value || [];
  }

  @computed get sessions() {
    return this.loadSessionsQuery.value || [];
  }

  @computed get sessionsSortedByDate() {
    return sortSessionsByDate(this.sessions);
  }

  @computed public get values() {
    return this.loadValuesQuery.value || [];
  }

  @computed get valuesInventory() {
    return (
      this.loadValuesInventoryQuery.value || {
        assigned: false,
      }
    );
  }

  // UI states
  @computed get loadPatientState() {
    return this.loadPatientDataQuery;
  }

  @computed get loadActivitiesState() {
    return this.loadActivitiesQuery;
  }

  @computed get loadActivityLogsState() {
    return this.loadActivityLogsQuery;
  }

  @computed get loadActivitySchedulesState() {
    return this.loadActivitySchedulesQuery;
  }

  @computed get loadAssessmentsState() {
    return this.loadAssessmentsQuery;
  }

  @computed get loadAssessmentLogsState() {
    return this.loadAssessmentLogsQuery;
  }

  @computed get loadCaseReviewsState() {
    return this.loadCaseReviewsQuery;
  }

  @computed get loadClinicalHistoryState() {
    return this.loadClinicalHistoryQuery;
  }

  @computed get loadMoodLogsState() {
    return this.loadMoodLogsQuery;
  }

  @computed get loadProfileState() {
    return this.loadProfileQuery;
  }

  @computed get loadReviewMarksState() {
    return this.loadReviewMarksQuery;
  }

  @computed get loadSafetyPlanState() {
    return this.loadSafetyPlanQuery;
  }

  @computed get loadScheduledActivitiesState() {
    return this.loadScheduledActivitiesQuery;
  }

  @computed get loadScheduledAssessmentsState() {
    return this.loadScheduledAssessmentsQuery;
  }

  @computed get loadSessionsState() {
    return this.loadSessionsQuery;
  }

  @computed public get loadValuesState() {
    return this.loadValuesQuery;
  }

  @computed get loadValuesInventoryState() {
    return this.loadValuesInventoryQuery;
  }

  // Helpers
  public getActivitiesByLifeAreaId(lifeAreaId: string) {
    return this.activities.filter((current) => {
      if (!current.valueId) {
        return false;
      }

      const value = this.getValueById(current.valueId);
      if (!value) {
        return false;
      }

      return value.lifeAreaId == lifeAreaId;
    });
  }

  public getActivitiesByValueId(valueId: string) {
    return this.activities.filter((current) => {
      if (!current.valueId) {
        return false;
      }

      return current.valueId == valueId;
    });
  }

  public getActivityById(activityId: string) {
    return this.activities.find((current) => current.activityId == activityId);
  }

  public getAssessmentLogById(assessmentLogId: string) {
    return this.assessmentLogs.find(
      (current) => current.assessmentLogId == assessmentLogId,
    );
  }

  public getCaseReviewById(caseReviewId: string) {
    return this.caseReviews.find(
      (current) => current.caseReviewId == caseReviewId,
    );
  }

  public getMoodLogById(moodLogId: string) {
    return this.moodLogs.find((current) => current.moodLogId == moodLogId);
  }

  public getRecentEntryActivityById(activityId: string) {
    return this.recentEntryActivities?.find(
      (current) => current.activityId == activityId,
    );
  }

  public getRecentEntryAssessmentLogById(assessmentLogId: string) {
    return this.recentEntryAssessmentLogsSortedByDateAndTimeDescending?.find(
      (current) => current.assessmentLogId == assessmentLogId,
    );
  }

  public getRecentEntryValueById(valueId: string) {
    return this.recentEntryValues?.find(
      (current) => current.valueId == valueId,
    );
  }

  public getRecentEntryAssessmentLogsSortedByDateAndTimeDescendingByAssessmentId(
    assessmentId: string,
  ) {
    return this.recentEntryAssessmentLogsSortedByDateAndTimeDescending?.filter(
      (l) => l.assessmentId == assessmentId,
    );
  }

  public getRecentEntryMoodLogById(moodLogId: string) {
    return this.recentEntryMoodLogsSortedByDateAndTimeDescending?.find(
      (current) => current.moodLogId == moodLogId,
    );
  }

  public getRecentEntryScheduledActivityById(scheduledActivityId: string) {
    return this.recentEntryScheduledActivitiesSortedByDateAndTimeDescending?.find(
      (current) => current.scheduledActivityId == scheduledActivityId,
    );
  }

  public getScheduledActivityById(scheduledActivityId: string) {
    return this.scheduledActivities.find(
      (current) => current.scheduledActivityId == scheduledActivityId,
    );
  }

  public getSessionById(sessionId: string) {
    return this.sessions.find((current) => current.sessionId == sessionId);
  }

  public getValueById(valueId: string) {
    return this.values.find((current) => current.valueId == valueId);
  }

  // Filters
  @computed public get valuesWithoutActivity(): IValue[] {
    return this.values.filter(
      (value) =>
        !value.valueId ||
        this.getActivitiesByValueId(value.valueId).length === 0,
    );
  }

  // Data load/save
  @action.bound
  public async load(
    getToken?: () => string | undefined,
    onUnauthorized?: () => void,
  ) {
    if (getToken) {
      this.patientService.applyAuth(getToken, onUnauthorized);
    }

    // Don't load if it's already loading
    if (this.loadProfileState.pending) {
      return;
    }

    // Use this to make a single patient call to load everything
    const initialLoad = () =>
      this.patientService.getPatient().then((patient) => {
        this.loadActivitiesQuery.fromPromise(
          Promise.resolve(patient.activities),
        );
        this.loadActivityLogsQuery.fromPromise(
          Promise.resolve(patient.activityLogs),
        );
        this.loadActivitySchedulesQuery.fromPromise(
          Promise.resolve(patient.activitySchedules),
        );
        this.loadAssessmentsQuery.fromPromise(
          Promise.resolve(patient.assessments),
        );
        this.loadAssessmentLogsQuery.fromPromise(
          Promise.resolve(patient.assessmentLogs),
        );
        this.loadCaseReviewsQuery.fromPromise(
          Promise.resolve(patient.caseReviews),
        );
        this.loadClinicalHistoryQuery.fromPromise(
          Promise.resolve(patient.clinicalHistory),
        );
        this.loadMoodLogsQuery.fromPromise(Promise.resolve(patient.moodLogs));
        this.loadProfileQuery.fromPromise(Promise.resolve(patient.profile));
        this.loadReviewMarksQuery.fromPromise(
          Promise.resolve(patient.reviewMarks),
        );
        this.loadSafetyPlanQuery.fromPromise(
          Promise.resolve(patient.safetyPlan),
        );
        this.loadScheduledActivitiesQuery.fromPromise(
          Promise.resolve(patient.scheduledActivities),
        );
        this.loadScheduledAssessmentsQuery.fromPromise(
          Promise.resolve(patient.scheduledAssessments),
        );
        this.loadSessionsQuery.fromPromise(Promise.resolve(patient.sessions));
        this.loadValuesQuery.fromPromise(Promise.resolve(patient.values));
        this.loadValuesInventoryQuery.fromPromise(
          Promise.resolve(patient.valuesInventory),
        );

        return patient;
      });

    await this.loadAndLogQuery<IPatient>(
      initialLoad,
      this.loadPatientDataQuery,
    );

    // Use this in case we want to call each document separately
    // await Promise.all([
    //     this.loadAndLogQuery<IPatient>(this.patientService.getPatient, this.loadPatientDataQuery),
    //     this.loadAndLogQuery<IPatientProfile>(this.patientService.getProfile, this.loadProfileQuery),
    //     this.loadAndLogQuery<IClinicalHistory>(
    //         this.patientService.getClinicalHistory,
    //         this.loadClinicalHistoryQuery,
    //     ),
    //     this.loadAndLogQuery<IValuesInventory>(
    //         this.patientService.getValuesInventory,
    //         this.loadValuesInventoryQuery,
    //     ),
    //     this.loadAndLogQuery<ISafetyPlan>(this.patientService.getSafetyPlan, this.loadSafetyPlanQuery),
    //     this.loadAndLogQuery<ISession[]>(this.patientService.getSessions, this.loadSessionsQuery),
    //     this.loadAndLogQuery<ICaseReview[]>(this.patientService.getCaseReviews, this.loadCaseReviewsQuery),
    //     this.loadAndLogQuery<IAssessment[]>(this.patientService.getAssessments, this.loadAssessmentsQuery),
    //     this.loadAndLogQuery<IActivity[]>(this.patientService.getActivities, this.loadActivitiesQuery),
    //     this.loadAndLogQuery<IScheduledAssessment[]>(
    //         this.patientService.getScheduledAssessments,
    //         this.loadScheduledAssessmentsQuery,
    //     ),
    //     this.loadAndLogQuery<IScheduledActivity[]>(
    //         this.patientService.getScheduledActivities,
    //         this.loadScheduledActivitiesQuery,
    //     ),
    //     this.loadAndLogQuery<IAssessmentLog[]>(this.patientService.getAssessmentLogs, this.loadAssessmentLogsQuery),
    //     this.loadAndLogQuery<IMoodLog[]>(this.patientService.getMoodLogs, this.loadMoodLogsQuery),
    //     this.loadAndLogQuery<IActivityLog[]>(this.patientService.getActivityLogs, this.loadActivityLogsQuery),
    // ]);
  }

  // Assessments
  @action.bound
  public async addAssessmentLog(assessmentLog: IAssessmentLog) {
    const promise = this.patientService
      .addAssessmentLog({
        ...toJS(assessmentLog),
      })
      .then((addedLog) => {
        return this.assessmentLogs.slice().concat([addedLog]);
      });

    await this.loadAndLogQuery<IAssessmentLog[]>(
      () => promise,
      this.loadAssessmentLogsQuery,
      this.onAssessmentLogsConflict,
    );
  }

  @action.bound
  public async updateAssessment(assessment: IAssessment) {
    const found = this.assessments.find(
      (a) => a.assessmentId == assessment.assessmentId,
    );

    console.assert(!!found, "Assessment not found");

    if (found) {
      const promise = this.patientService
        .updateAssessment({
          ...toJS(found),
          ...assessment,
        })
        .then((updatedAssessment) => {
          const existing = this.assessments.find(
            (a) => a.assessmentId == updatedAssessment.assessmentId,
          );
          logger.assert(!!existing, "Assessment not found when expected");

          if (!!existing) {
            Object.assign(existing, updatedAssessment);
            return this.assessments;
          } else {
            return this.assessments.slice().concat([updatedAssessment]);
          }
        });

      await this.loadAndLogQuery<IAssessment[]>(
        () => promise,
        this.loadAssessmentsQuery,
        this.onAssessmentConflict,
      );
    }
  }

  @action.bound
  public async updateAssessmentLog(assessmentLog: IAssessmentLog) {
    const promise = this.patientService
      .updateAssessmentLog({
        ...toJS(assessmentLog),
      })
      .then((updatedAssessmentLog) => {
        const logsCopy = this.assessmentLogs.slice();
        const existingIdx = this.assessmentLogs.findIndex(
          (r) => r.assessmentLogId == updatedAssessmentLog.assessmentLogId,
        );
        logger.assert(
          existingIdx >= 0,
          "Assessment log not found when expected",
        );

        if (existingIdx >= 0) {
          logsCopy.splice(existingIdx, 1, updatedAssessmentLog);
          return logsCopy;
        } else {
          return this.assessmentLogs.slice().concat([updatedAssessmentLog]);
        }
      });

    await this.loadAndLogQuery<IAssessmentLog[]>(
      () => promise,
      this.loadAssessmentLogsQuery,
      this.onAssessmentLogsConflict,
    );
  }

  // Assignments
  @action.bound
  public async assignAssessment(assessmentId: string) {
    const found = this.assessments.find((a) => a.assessmentId == assessmentId);

    console.assert(!!found, "Assessment not found");

    if (found) {
      return this.updateAssessment({
        ...toJS(found),
        assessmentId,
        assigned: true,
        assignedDateTime: new Date(),
        frequency: found.frequency || "Every 2 weeks",
        dayOfWeek: found.dayOfWeek || "Monday",
      });
    }
  }

  @action.bound
  public async cancelAssessment(assessmentId: string) {
    const found = this.assessments.find((a) => a.assessmentId == assessmentId);

    console.assert(!!found, "Assessment not found");

    if (found) {
      return this.updateAssessment({
        ...toJS(found),
        assessmentId,
        assigned: false,
        assignedDateTime: new Date(),
        frequency: undefined,
        dayOfWeek: undefined,
      });
    }
  }

  @action.bound
  public async assignSafetyPlan() {
    const promise = this.patientService.updateSafetyPlan({
      ...toJS(this.safetyPlan),
      assigned: true,
      assignedDateTime: new Date(),
    });

    await this.loadAndLogQuery<ISafetyPlan>(
      () => promise,
      this.loadSafetyPlanQuery,
      onSingletonConflict("safetyplan"),
    );
  }

  @action.bound
  public async assignValuesInventory() {
    const promise = this.patientService.updateValuesInventory({
      ...toJS(this.valuesInventory),
      assigned: true,
      assignedDateTime: new Date(),
    });

    await this.loadAndLogQuery<IValuesInventory>(
      () => promise,
      this.loadValuesInventoryQuery,
      onSingletonConflict("valuesinventory"),
    );
  }

  // Case Review
  @action.bound
  public async addCaseReview(caseReview: ICaseReview) {
    const promise = this.patientService
      .addCaseReview({
        ...toJS(caseReview),
        consultingPsychiatrist: {
          providerId: caseReview.consultingPsychiatrist.providerId,
          name: caseReview.consultingPsychiatrist.name,
          role: "psychiatrist",
        },
      })
      .then((addedReview) => {
        return this.caseReviews.slice().concat([addedReview]);
      });

    await this.loadAndLogQuery<ICaseReview[]>(
      () => promise,
      this.loadCaseReviewsQuery,
      this.onCaseReviewConflict,
    );
  }

  @action.bound
  public async updateCaseReview(caseReview: ICaseReview) {
    const promise = this.patientService
      .updateCaseReview({
        ...toJS(caseReview),
        consultingPsychiatrist: {
          providerId: caseReview.consultingPsychiatrist.providerId,
          name: caseReview.consultingPsychiatrist.name,
          role: "psychiatrist",
        },
      })
      .then((updatedReview) => {
        const existing = !!updatedReview.caseReviewId
          ? this.getCaseReviewById(updatedReview.caseReviewId)
          : undefined;
        logger.assert(!!existing, "Case review not found when expected");

        if (!!existing) {
          Object.assign(existing, updatedReview);
          return this.caseReviews;
        } else {
          return this.caseReviews.slice().concat([updatedReview]);
        }
      });

    await this.loadAndLogQuery<ICaseReview[]>(
      () => promise,
      this.loadCaseReviewsQuery,
      this.onCaseReviewConflict,
    );
  }

  // Clinical History
  @action.bound
  public async updateClinicalHistory(clinicalHistory: IClinicalHistory) {
    const promise = this.patientService.updateClinicalHistory({
      ...toJS(this.clinicalHistory),
      ...toJS(clinicalHistory),
      currentTreatmentRegimen: Object.assign(
        {},
        ...cancerTreatmentRegimenValues.map((x) => ({
          [x]: !!clinicalHistory.currentTreatmentRegimen?.[x],
        })),
      ),
    });

    await this.loadAndLogQuery<IClinicalHistory>(
      () => promise,
      this.loadClinicalHistoryQuery,
      onSingletonConflict("clinicalhistory"),
    );
  }

  // Patient Profile
  @action.bound
  public async updateProfile(patientProfile: IPatientProfile) {
    const promise = this.patientService.updateProfile({
      ...toJS(this.profile),
      ...toJS(patientProfile),
      race: Object.assign(
        {},
        ...patientRaceValues.map((x) => ({ [x]: !!patientProfile.race?.[x] })),
      ),
      discussionFlag: Object.assign(
        {},
        ...discussionFlagValues.map((x) => ({
          [x]: !!patientProfile.discussionFlag?.[x],
        })),
      ),
      primaryCareManager: patientProfile.primaryCareManager
        ? {
            name: patientProfile.primaryCareManager?.name,
            providerId: patientProfile.primaryCareManager?.providerId,
            role: patientProfile.primaryCareManager?.role,
          }
        : undefined,
    });

    await this.loadAndLogQuery<IPatientProfile>(
      () => promise,
      this.loadProfileQuery,
      onSingletonConflict("profile"),
    );
  }

  // Recent Entry Review
  @action.bound
  public async addReviewMark(reviewMark: IReviewMark) {
    const promise = this.patientService
      .addReviewMark(toJS(reviewMark))
      .then((addedReview) => {
        return this.reviewMarks.slice().concat([addedReview]);
      });

    await this.loadAndLogQuery<IReviewMark[]>(
      () => promise,
      this.loadReviewMarksQuery,
      this.onReviewMarkConflict,
    );
  }

  // Session
  @action.bound
  public async addSession(session: ISession) {
    const promise = this.patientService
      .addSession(toJS(session))
      .then((addedSession) => {
        return this.sessions.slice().concat([addedSession]);
      });

    await this.loadAndLogQuery<ISession[]>(
      () => promise,
      this.loadSessionsQuery,
      this.onSessionConflict,
    );
  }

  @action.bound
  public async updateSession(session: ISession) {
    const promise = this.patientService
      .updateSession({
        ...toJS(session),
        behavioralStrategyChecklist: Object.assign(
          {},
          ...behavioralStrategyChecklistValues.map((x) => ({
            [x]: !!session.behavioralStrategyChecklist?.[x],
          })),
        ),
        behavioralActivationChecklist: Object.assign(
          {},
          ...behavioralActivationChecklistValues.map((x) => ({
            [x]: !!session.behavioralActivationChecklist?.[x],
          })),
        ),
      })
      .then((updatedSession) => {
        const existing = !!updatedSession.sessionId
          ? this.getSessionById(updatedSession.sessionId)
          : undefined;
        logger.assert(!!existing, "Session not found when expected");

        if (!!existing) {
          Object.assign(existing, updatedSession);
          return this.sessions;
        } else {
          return this.sessions.slice().concat([updatedSession]);
        }
      });

    await this.loadAndLogQuery<ISession[]>(
      () => promise,
      this.loadSessionsQuery,
      this.onSessionConflict,
    );
  }

  private onAssessmentConflict = (responseData?: any) => {
    return onArrayConflict(
      "assessment",
      "assessmentId",
      () => this.assessments,
      logger,
    )(responseData);
  };

  private onAssessmentLogsConflict = (responseData?: any) => {
    return onArrayConflict(
      "assessmentlog",
      "assessmentLogId",
      () => this.assessmentLogs,
      logger,
    )(responseData);
  };

  private onCaseReviewConflict = (responseData?: any) => {
    return onArrayConflict(
      "casereview",
      "caseReviewId",
      () => this.caseReviews,
      logger,
    )(responseData);
  };

  private onReviewMarkConflict = (responseData?: any) => {
    return onArrayConflict(
      "reviewmark",
      "reviewMarkId",
      () => this.reviewMarks,
      logger,
    )(responseData);
  };

  private onSessionConflict = (responseData?: any) => {
    return onArrayConflict(
      "session",
      "sessionId",
      () => this.sessions,
      logger,
    )(responseData);
  };
}
