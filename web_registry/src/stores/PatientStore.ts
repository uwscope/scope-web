import { differenceInYears, subDays } from "date-fns";
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
  sortScheduledActivitiesByDateAndTime,
  sortSessionsByDate,
  sortValuesByDateAndTime,
} from "shared/sorting";
import {
  getLoadAndLogQuery,
  onArrayConflict,
  onSingletonConflict,
} from "shared/stores";
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

  // Recent patient interaction properties
  readonly recentInteractionCaseloadSummary: string | undefined;
  readonly recentInteractionCutoffDateTime: Date;
  readonly recentActivities: IActivity[] | undefined;
  readonly recentActivityLogsSortedByDateAndTimeDescending:
  | IActivityLog[]
  | undefined;
  readonly recentAssessmentLogsSortedByDateAndTimeDescending:
  | IAssessmentLog[]
  | undefined;
  readonly recentMoodLogsSortedByDateAndTimeDescending: IMoodLog[] | undefined;
  readonly recentSafetyPlan: ISafetyPlan | undefined;
  readonly recentScheduledActivitiesSortedByDateAndTimeDescending:
  | IScheduledActivity[]
  | undefined;
  readonly recentValues: IValue[] | undefined;

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
  readonly scheduledActivitiesSortedByDateAndTimeDescending: IScheduledActivity[];
  readonly valuesSortedByDateAndTimeDescending: IValue[];

  // Helpers
  getActivitiesByLifeAreaId: (lifeAreaId: string) => IActivity[];
  getActivitiesByValueId: (valueId: string) => IActivity[];
  getActivitiesWithoutValueId: () => IActivity[];
  getActivityById: (activityId: string) => IActivity | undefined;
  getAssessmentLogById: (assessmentLogId: string) => IAssessmentLog | undefined;
  getCaseReviewById: (caseReviewId: string) => ICaseReview | undefined;
  getRecentActivityById: (
    activityId: string,
  ) => IActivity | undefined;
  getRecentAssessmentLogById: (
    assessmentLogId: string,
  ) => IAssessmentLog | undefined;
  getRecentValueById: (
    valueId: string,
  ) => IValue | undefined;
  recentAssessmentLogsSortedByDateAndTimeDescendingByAssessmentId: (
    assessmentId: string,
  ) => IAssessmentLog[] | undefined;
  getRecentMoodLogById: (moodLogId: string) => IMoodLog | undefined;
  getRecentScheduledActivityById: (
    scheduledActivityId: string,
  ) => IScheduledActivity | undefined;
  getSessionById: (sessionId: string) => ISession | undefined;
  getValueById: (valueId: string) => IValue | undefined;
  getValuesWithoutActivity: () => IValue[] | undefined;

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

  @computed get scheduledActivitiesSortedByDateAndTimeDescending() {
    return sortScheduledActivitiesByDateAndTime(
      this.scheduledActivities,
      SortDirection.DESCENDING,
    );
  }

  @computed get valuesSortedByDateAndTimeDescending() {
    return sortValuesByDateAndTime(
      this.values,
      SortDirection.DESCENDING,
    );
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

  @computed get recentInteractionCaseloadSummary() {
    const recentInteraction: boolean =
      (!!this.recentActivities && this.recentActivities.length > 0) ||
      (!!this.recentActivityLogsSortedByDateAndTimeDescending &&
        this.recentActivityLogsSortedByDateAndTimeDescending.length > 0) ||
      (!!this.recentAssessmentLogsSortedByDateAndTimeDescending &&
        this.recentAssessmentLogsSortedByDateAndTimeDescending.length > 0) ||
      (!!this.recentMoodLogsSortedByDateAndTimeDescending &&
        this.recentMoodLogsSortedByDateAndTimeDescending.length > 0) ||
      !!this.recentSafetyPlan ||
      (!!this.recentScheduledActivitiesSortedByDateAndTimeDescending &&
        this.recentScheduledActivitiesSortedByDateAndTimeDescending.length >
        0) ||
      (!!this.recentValues && this.recentValues.length > 0);

    return recentInteraction ? "New" : undefined;
  }

  @computed get recentInteractionCutoffDateTime() {
    // Initially, stub the function to return now minus two weeks.
    // Eventually, this will be calculated based on when a social worker marks a patient as reviewed.
    let cutoffDateTime = new Date();
    cutoffDateTime = subDays(cutoffDateTime, 14);

    return cutoffDateTime;
  }

  @computed get recentActivities() {
    if (this.activities.length === 0) {
      return undefined;
    } else {
      return this.activities.filter((a) => {
        return a.editedDateTime >= this.recentInteractionCutoffDateTime;
      });
    }
  }

  @computed get recentActivityLogsSortedByDateAndTimeDescending() {
    const indexEnd = this.activityLogsSortedByDateAndTimeDescending.findIndex(
      (a) => a.recordedDateTime < this.recentInteractionCutoffDateTime,
    );

    if (indexEnd < 0) {
      return this.activityLogsSortedByDateAndTimeDescending.slice();
    } else if (indexEnd === 0) {
      return undefined;
    } else {
      return this.activityLogsSortedByDateAndTimeDescending.slice(0, indexEnd);
    }
  }

  @computed get recentAssessmentLogsSortedByDateAndTimeDescending() {
    const indexEnd = this.assessmentLogsSortedByDateAndTimeDescending.findIndex(
      (a) => a.recordedDateTime < this.recentInteractionCutoffDateTime,
    );

    if (indexEnd < 0) {
      return this.assessmentLogsSortedByDateAndTimeDescending.slice();
    } else if (indexEnd === 0) {
      return undefined;
    } else {
      return this.assessmentLogsSortedByDateAndTimeDescending.slice(
        0,
        indexEnd,
      );
    }
  }

  @computed get recentMoodLogsSortedByDateAndTimeDescending() {
    const indexEnd = this.moodLogsSortedByDateAndTimeDescending.findIndex(
      (a) => a.recordedDateTime < this.recentInteractionCutoffDateTime,
    );

    if (indexEnd < 0) {
      return this.moodLogsSortedByDateAndTimeDescending.slice();
    } else if (indexEnd === 0) {
      return undefined;
    } else {
      return this.moodLogsSortedByDateAndTimeDescending.slice(0, indexEnd);
    }
  }

  @computed get recentSafetyPlan() {
    // The default empty safety plan will not have a lastUpdatedDateTime
    if (
      !!this.safetyPlan.lastUpdatedDateTime &&
      this.safetyPlan.lastUpdatedDateTime >=
      this.recentInteractionCutoffDateTime
    ) {
      return this.safetyPlan;
    }
    return undefined;
  }

  @computed get recentScheduledActivitiesSortedByDateAndTimeDescending() {
    const indexEnd =
      this.scheduledActivitiesSortedByDateAndTimeDescending.findIndex(
        (a) => a.dueDateTime < this.recentInteractionCutoffDateTime,
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

  @computed get recentValues() {
    if (this.values.length === 0) {
      return undefined;
    } else {
      return this.values.filter((a) => {
        return a.editedDateTime >= this.recentInteractionCutoffDateTime;
      });
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

  public getActivitiesWithoutValueId() {
    return this.activities.filter((current) => {
      return !current.valueId;
    });
  }

  public getActivityById(activityId: string) {
    return this.activities.find((current) => current.activityId == activityId);;
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

  public getRecentActivityById(activityId: string) {
    return this.recentActivities?.find(
      (current) => current.activityId == activityId,
    );
  }

  public getRecentAssessmentLogById(assessmentLogId: string) {
    return this.recentAssessmentLogsSortedByDateAndTimeDescending?.find(
      (current) => current.assessmentLogId == assessmentLogId,
    );
  }

  public getRecentValueById(valueId: string) {
    return this.recentValues?.find(
      (current) => current.valueId == valueId,
    );
  }

  public recentAssessmentLogsSortedByDateAndTimeDescendingByAssessmentId(
    assessmentId: string,
  ) {
    return this.recentAssessmentLogsSortedByDateAndTimeDescending?.filter(
      (l) => l.assessmentId == assessmentId,
    );
  }

  public getRecentMoodLogById(moodLogId: string) {
    return this.recentMoodLogsSortedByDateAndTimeDescending?.find(
      (current) => current.moodLogId == moodLogId,
    );
  }

  public getRecentScheduledActivityById(scheduledActivityId: string) {
    return this.recentScheduledActivitiesSortedByDateAndTimeDescending?.find(
      (current) => current.scheduledActivityId == scheduledActivityId,
    );
  }

  public getSessionById(sessionId: string) {
    return this.sessions.find((current) => current.sessionId == sessionId);
  }

  public getValueById(valueId: string) {
    return this.values.find((current) => current.valueId == valueId);
  }

  public getValuesWithoutActivity() {
    // NOTE: Verify why .valueId is optional.
    return this.values.filter((value) => this.getActivitiesByValueId(value.valueId as string).length === 0);
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

  private onSessionConflict = (responseData?: any) => {
    return onArrayConflict(
      "session",
      "sessionId",
      () => this.sessions,
      logger,
    )(responseData);
  };
}
