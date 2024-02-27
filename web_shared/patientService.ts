import _ from "lodash";
import { getLogger } from "shared/logger";
import { IServiceBase, ServiceBase } from "shared/serviceBase";
import {
  IPatientProfileRequest,
  IPatientProfileResponse,
  IPatientResponse,
  IValuesInventoryResponse,
  IValuesInventoryRequest,
  IClinicalHistoryRequest,
  IClinicalHistoryResponse,
  ISessionListResponse,
  ISessionResponse,
  ICaseReviewListResponse,
  ISessionRequest,
  ICaseReviewResponse,
  ICaseReviewRequest,
  IAssessmentLogListResponse,
  IAssessmentListResponse,
  IAssessmentLogRequest,
  IAssessmentLogResponse,
  IAssessmentResponse,
  IAssessmentRequest,
  ISafetyPlanResponse,
  ISafetyPlanRequest,
  IScheduledActivityListResponse,
  IActivityRequest,
  IActivityResponse,
  IActivityListResponse,
  IActivityLogListResponse,
  IActivityLogResponse,
  IActivityLogRequest,
  IActivityScheduleRequest,
  IActivityScheduleResponse,
  IActivityScheduleListResponse,
  IMoodLogRequest,
  IMoodLogResponse,
  IMoodLogListResponse,
  IScheduledAssessmentListResponse,
  IValueRequest,
  IValueResponse,
  IValueListResponse,
  IPushSubscriptionListResponse,
  IPushSubscriptionResponse,
  IPushSubscriptionRequest,
} from 'shared/serviceTypes';
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
  IPatientConfig,
  IPatientProfile,
  IPushSubscription,
  ISafetyPlan,
  IScheduledActivity,
  IScheduledAssessment,
  ISession,
  IValue,
  IValuesInventory,
} from 'shared/types';

export interface IPatientService extends IServiceBase {
  // Dynamic
  getPatientConfig(): Promise<IPatientConfig>;

  // Singletons
  getPatient(): Promise<IPatient>;

  getProfile(): Promise<IPatientProfile>;
  updateProfile(profile: IPatientProfile): Promise<IPatientProfile>;

  getValuesInventory(): Promise<IValuesInventory>;
  updateValuesInventory(values: IValuesInventory): Promise<IValuesInventory>;

  getSafetyPlan(): Promise<ISafetyPlan>;
  updateSafetyPlan(safetyPlan: ISafetyPlan): Promise<ISafetyPlan>;

  getClinicalHistory(): Promise<IClinicalHistory>;
  updateClinicalHistory(history: IClinicalHistory): Promise<IClinicalHistory>;

  // Arrays/sets
  getSessions(): Promise<ISession[]>;
  addSession(session: ISession): Promise<ISession>;
  updateSession(session: ISession): Promise<ISession>;

  getCaseReviews(): Promise<ICaseReview[]>;
  addCaseReview(caseReview: ICaseReview): Promise<ICaseReview>;
  updateCaseReview(caseReview: ICaseReview): Promise<ICaseReview>;

  getScheduledActivities(): Promise<IScheduledActivity[]>;

  getActivities(): Promise<IActivity[]>;
  addActivity(activity: IActivity): Promise<IActivity>;
  deleteActivity(activity: IActivity): Promise<IActivity>;
  updateActivity(activity: IActivity): Promise<IActivity>;

  getActivitySchedules(): Promise<IActivitySchedule[]>;
  addActivitySchedule(
    activitySchedule: IActivitySchedule,
  ): Promise<IActivitySchedule>;
  deleteActivitySchedule(
    activitySchedule: IActivitySchedule,
  ): Promise<IActivitySchedule>;
  updateActivitySchedule(
    activitySchedule: IActivitySchedule,
  ): Promise<IActivitySchedule>;

  getActivityLogs(): Promise<IActivityLog[]>;
  addActivityLog(activityLog: IActivityLog): Promise<IActivityLog>;

  getScheduledAssessments(): Promise<IScheduledAssessment[]>;

  getAssessments(): Promise<IAssessment[]>;
  updateAssessment(assessment: IAssessment): Promise<IAssessment>;

  getAssessmentLogs(): Promise<IAssessmentLog[]>;
  addAssessmentLog(assessmentLog: IAssessmentLog): Promise<IAssessmentLog>;
  updateAssessmentLog(assessmentLog: IAssessmentLog): Promise<IAssessmentLog>;

  getMoodLogs(): Promise<IMoodLog[]>;
  addMoodLog(moodLog: IMoodLog): Promise<IMoodLog>;

  getPushSubscriptions(): Promise<IPushSubscription[]>;
  addPushSubscription(pushSubscription: IPushSubscription): Promise<IPushSubscription>;
  deletePushSubscription(pushSubscription: IPushSubscription): Promise<IPushSubscription>;
  updatePushSubscription(pushSubscription: IPushSubscription): Promise<IPushSubscription>;

  getValues(): Promise<IValue[]>;
  addValue(value: IValue): Promise<IValue>;
  deleteValue(value: IValue): Promise<IValue>;
  updateValue(value: IValue): Promise<IValue>;
}

const logger = getLogger("patientService");

class PatientService extends ServiceBase implements IPatientService {
  constructor(baseUrl: string) {
    super(baseUrl);
  }

  public async getPatient(): Promise<IPatient> {
    const response = await this.axiosInstance.get<IPatientResponse>("");
    return response.data?.patient;
  }

  public async getProfile(): Promise<IPatientProfile> {
    const response =
      await this.axiosInstance.get<IPatientProfileResponse>(`/profile`);
    return response.data?.profile;
  }

  public async updateProfile(
    profile: IPatientProfile,
  ): Promise<IPatientProfile> {
    logger.assert(
      (profile as any)._type === "profile",
      `invalid _type for patient profile: ${(profile as any)._type}`,
    );

    (profile as any)._type = "profile";
    if (!!profile.primaryCareManager) {
      (profile.primaryCareManager as any)._type = "providerIdentity";
    }

    const response = await this.axiosInstance.put<IPatientProfileResponse>(
      `/profile`,
      {
        profile,
      } as IPatientProfileRequest,
    );

    return response.data?.profile;
  }

  public async getClinicalHistory(): Promise<IClinicalHistory> {
    const response =
      await this.axiosInstance.get<IClinicalHistoryResponse>(
        `/clinicalhistory`,
      );
    return response.data?.clinicalhistory;
  }

  public async updateClinicalHistory(
    history: IClinicalHistory,
  ): Promise<IClinicalHistory> {
    logger.assert(
      (history as any)._type === "clinicalHistory",
      `invalid _type for patient clinical history: ${(history as any)._type}`,
    );

    (history as any)._type = "clinicalHistory";
    const response = await this.axiosInstance.put<IClinicalHistoryResponse>(
      `/clinicalhistory`,
      {
        clinicalhistory: history,
      } as IClinicalHistoryRequest,
    );

    return response.data?.clinicalhistory;
  }

  public async getValuesInventory(): Promise<IValuesInventory> {
    const response =
      await this.axiosInstance.get<IValuesInventoryResponse>(
        `/valuesinventory`,
      );
    return response.data?.valuesinventory;
  }

  public async updateValuesInventory(
    inventory: IValuesInventory,
  ): Promise<IValuesInventory> {
    logger.assert(
      (inventory as any)._type === "valuesInventory",
      `invalid _type for values inventory: ${(inventory as any)._type}`,
    );

    (inventory as any)._type = "valuesInventory";
    const response = await this.axiosInstance.put<IValuesInventoryResponse>(
      `/valuesinventory`,
      {
        valuesinventory: inventory,
      } as IValuesInventoryRequest,
    );
    return response.data?.valuesinventory;
  }

  public async getSafetyPlan(): Promise<ISafetyPlan> {
    const response =
      await this.axiosInstance.get<ISafetyPlanResponse>(`/safetyplan`);
    return response.data?.safetyplan;
  }

  public async updateSafetyPlan(safetyPlan: ISafetyPlan): Promise<ISafetyPlan> {
    logger.assert(
      (safetyPlan as any)._type === "safetyPlan",
      `invalid _type for values safety plan: ${(safetyPlan as any)._type}`,
    );

    (safetyPlan as any)._type = "safetyPlan";
    const response = await this.axiosInstance.put<ISafetyPlanResponse>(
      `/safetyplan`,
      {
        safetyplan: safetyPlan,
      } as ISafetyPlanRequest,
    );
    return response.data?.safetyplan;
  }

  public async getSessions(): Promise<ISession[]> {
    const response =
      await this.axiosInstance.get<ISessionListResponse>(`/sessions`);
    return response.data?.sessions;
  }

  public async addSession(session: ISession): Promise<ISession> {
    (session as any)._type = "session";

    logger.assert(
      (session as any)._rev == undefined,
      "_rev should not be in the request data",
    );
    logger.assert(
      (session as any)._set_id == undefined,
      "_set_id should not be in the request data",
    );

    const response = await this.axiosInstance.post<ISessionResponse>(
      `/sessions`,
      { session } as ISessionRequest,
    );
    return response.data?.session;
  }

  public async updateSession(session: ISession): Promise<ISession> {
    logger.assert(
      (session as any)._type === "session",
      `invalid _type for session: ${(session as any)._type}`,
    );
    logger.assert(
      (session as any)._rev != undefined,
      "_rev should be in the request data",
    );
    logger.assert(
      (session as any)._set_id != undefined,
      "_set_id should be in the request data",
    );

    (session as any)._type = "session";
    const response = await this.axiosInstance.put<ISessionResponse>(
      `/session/${session.sessionId}`,
      {
        session,
      } as ISessionRequest,
    );
    return response.data?.session;
  }

  public async getCaseReviews(): Promise<ICaseReview[]> {
    const response =
      await this.axiosInstance.get<ICaseReviewListResponse>(`/casereviews`);
    return response.data?.casereviews;
  }

  public async addCaseReview(review: ICaseReview): Promise<ICaseReview> {
    (review as any)._type = "caseReview";
    (review.consultingPsychiatrist as any)._type = "providerIdentity";

    logger.assert(
      (review as any)._rev == undefined,
      "_rev should not be in the request data",
    );
    logger.assert(
      (review as any)._set_id == undefined,
      "_set_id should not be in the request data",
    );

    const response = await this.axiosInstance.post<ICaseReviewResponse>(
      `/casereviews`,
      {
        casereview: review,
      } as ICaseReviewRequest,
    );
    return response.data?.casereview;
  }

  public async updateCaseReview(review: ICaseReview): Promise<ICaseReview> {
    (review.consultingPsychiatrist as any)._type = "providerIdentity";

    logger.assert(
      (review as any)._type === "caseReview",
      `invalid _type for case review: ${(review as any)._type}`,
    );
    logger.assert(
      (review as any)._rev != undefined,
      "_rev should be in the request data",
    );
    logger.assert(
      (review as any)._set_id != undefined,
      "_set_id should be in the request data",
    );

    (review as any)._type = "caseReview";
    const response = await this.axiosInstance.put<ICaseReviewResponse>(
      `/casereview/${review.caseReviewId}`,
      {
        casereview: review,
      } as ICaseReviewRequest,
    );
    return response.data?.casereview;
  }

  public async getScheduledActivities(): Promise<IScheduledActivity[]> {
    const response =
      await this.axiosInstance.get<IScheduledActivityListResponse>(
        `/scheduledactivities`,
      );
    return response.data?.scheduledactivities;
  }

  public async getActivities(): Promise<IActivity[]> {
    const response =
      await this.axiosInstance.get<IActivityListResponse>(`/activities`);
    return response.data?.activities;
  }

  public async addActivity(activity: IActivity): Promise<IActivity> {
    (activity as any)._type = "activity";

    const response = await this.axiosInstance.post<IActivityResponse>(
      `/activities`,
      {
        activity,
      } as IActivityRequest,
    );
    return response.data?.activity;
  }

  public async deleteActivity(activity: IActivity): Promise<IActivity> {
    logger.assert(
      (activity as any)._rev != undefined,
      "_rev should be in the request data",
    );
    const response = await this.axiosInstance.delete<IActivityResponse>(
      `/activity/${activity.activityId}`,
      {
        headers: {
          "If-Match": (activity as any)._rev,
        },
      },
    );
    return response.data?.activity;
  }

  public async updateActivity(activity: IActivity): Promise<IActivity> {
    logger.assert(
      (activity as any)._type === "activity",
      `invalid _type for activity: ${(activity as any)._type}`,
    );

    (activity as any)._type = "activity";
    const response = await this.axiosInstance.put<IActivityResponse>(
      `/activity/${activity.activityId}`,
      {
        activity,
      } as IActivityRequest,
    );
    return response.data?.activity;
  }

  public async getActivitySchedules(): Promise<IActivitySchedule[]> {
    const response =
      await this.axiosInstance.get<IActivityScheduleListResponse>(
        `/activityschedules`,
      );
    return response.data?.activityschedules;
  }

  public async addActivitySchedule(
    activitySchedule: IActivitySchedule,
  ): Promise<IActivitySchedule> {
    (activitySchedule as any)._type = "activitySchedule";

    const response = await this.axiosInstance.post<IActivityScheduleResponse>(
      `/activityschedules`,
      {
        activityschedule: activitySchedule,
      } as IActivityScheduleRequest,
    );
    return response.data?.activityschedule;
  }

  public async deleteActivitySchedule(
    activitySchedule: IActivitySchedule,
  ): Promise<IActivitySchedule> {
    logger.assert(
      (activitySchedule as any)._rev != undefined,
      "_rev should be in the request data",
    );
    const response = await this.axiosInstance.delete<IActivityScheduleResponse>(
      `/activityschedule/${activitySchedule.activityScheduleId}`,
      {
        headers: {
          "If-Match": (activitySchedule as any)._rev,
        },
      },
    );
    return response.data?.activityschedule;
  }

  public async updateActivitySchedule(
    activitySchedule: IActivitySchedule,
  ): Promise<IActivitySchedule> {
    logger.assert(
      (activitySchedule as any)._type === "activitySchedule",
      `invalid _type for activitySchedule: ${(activitySchedule as any)._type}`,
    );

    (activitySchedule as any)._type = "activitySchedule";
    const response = await this.axiosInstance.put<IActivityScheduleResponse>(
      `/activityschedule/${activitySchedule.activityScheduleId}`,
      {
        activityschedule: activitySchedule,
      } as IActivityScheduleRequest,
    );
    return response.data?.activityschedule;
  }

  public async getPatientConfig(): Promise<IPatientConfig> {
    const response = await this.axiosInstance.get<IPatientConfig>(`/summary`);
    return response.data;
  }

  public async getActivityLogs(): Promise<IActivityLog[]> {
    const response =
      await this.axiosInstance.get<IActivityLogListResponse>(`/activitylogs`);
    return response.data?.activitylogs;
  }

  public async addActivityLog(
    activityLog: IActivityLog,
  ): Promise<IActivityLog> {
    (activityLog as any)._type = "activityLog";

    const response = await this.axiosInstance.post<IActivityLogResponse>(
      `/activitylogs`,
      {
        activitylog: activityLog,
      } as IActivityLogRequest,
    );
    return response.data?.activitylog;
  }

  public async getScheduledAssessments(): Promise<IScheduledAssessment[]> {
    const response =
      await this.axiosInstance.get<IScheduledAssessmentListResponse>(
        `/scheduledassessments`,
      );
    return response.data?.scheduledassessments;
  }

  public async getAssessments(): Promise<IAssessment[]> {
    const response =
      await this.axiosInstance.get<IAssessmentListResponse>(`/assessments`);
    return response.data?.assessments;
  }

  public async updateAssessment(assessment: IAssessment): Promise<IAssessment> {
    logger.assert(
      (assessment as any)._type === "assessment",
      `invalid _type for assessment: ${(assessment as any)._type}`,
    );

    (assessment as any)._type = "assessment";
    const response = await this.axiosInstance.put<IAssessmentResponse>(
      `/assessment/${assessment.assessmentId}`,
      {
        assessment,
      } as IAssessmentRequest,
    );
    return response.data?.assessment;
  }

  public async getAssessmentLogs(): Promise<IAssessmentLog[]> {
    const response =
      await this.axiosInstance.get<IAssessmentLogListResponse>(
        `/assessmentlogs`,
      );
    return response.data?.assessmentlogs;
  }

  public async addAssessmentLog(
    assessmentLog: IAssessmentLog,
  ): Promise<IAssessmentLog> {
    (assessmentLog as any)._type = "assessmentLog";

    const response = await this.axiosInstance.post<IAssessmentLogResponse>(
      `/assessmentlogs`,
      {
        assessmentlog: assessmentLog,
      } as IAssessmentLogRequest,
    );
    return response.data?.assessmentlog;
  }

  public async updateAssessmentLog(
    assessmentLog: IAssessmentLog,
  ): Promise<IAssessmentLog> {
    (assessmentLog as any)._type = "assessmentLog";
    logger.assert(
      (assessmentLog as any)._rev != undefined,
      "_rev should be in the request data",
    );
    logger.assert(
      (assessmentLog as any)._set_id != undefined,
      "_set_id should be in the request data",
    );

    const response = await this.axiosInstance.put<IAssessmentLogResponse>(
      `/assessmentlog/${assessmentLog.assessmentLogId}`,
      {
        assessmentlog: assessmentLog,
      } as IAssessmentLogRequest,
    );

    return response.data?.assessmentlog;
  }

  public async getMoodLogs(): Promise<IMoodLog[]> {
    const response =
      await this.axiosInstance.get<IMoodLogListResponse>(`/moodlogs`);
    return response.data?.moodlogs;
  }

  public async addMoodLog(moodLog: IMoodLog): Promise<IMoodLog> {
    (moodLog as any)._type = "moodLog";

    const response = await this.axiosInstance.post<IMoodLogResponse>(`/moodlogs`, {
      moodlog: moodLog,
    } as IMoodLogRequest);
    return response.data?.moodlog;
  }

  public async addPushSubscription(pushSubscription: IPushSubscription): Promise<IPushSubscription> {
    (pushSubscription as any)._type = 'pushSubscription';

    const response = await this.axiosInstance.post<IPushSubscriptionResponse>(`/pushsubscriptions`, {
      pushsubscription: pushSubscription,
    } as IPushSubscriptionRequest);
    return response.data?.pushsubscription;
  }

  public async getPushSubscriptions(): Promise<IPushSubscription[]> {
    const response = await this.axiosInstance.get<IPushSubscriptionListResponse>(`/pushsubscriptions`);
    return response.data?.pushsubscriptions;
  }

  public async deletePushSubscription(pushSubscription: IPushSubscription): Promise<IPushSubscription> {
    logger.assert((pushSubscription as any)._rev != undefined, '_rev should be in the request data');
    const response = await this.axiosInstance.delete<IPushSubscriptionResponse>(
      `/pushsubscription/${pushSubscription.pushSubscriptionId}`,
      {
        headers: {
          'If-Match': (pushSubscription as any)._rev,
        },
      },
    );
    return response.data?.pushsubscription;
  }

  public async updatePushSubscription(pushSubscription: IPushSubscription): Promise<IPushSubscription> {
    (pushSubscription as any)._type = 'pushSubscription';
    logger.assert((pushSubscription as any)._rev != undefined, '_rev should be in the request data');
    logger.assert((pushSubscription as any)._set_id != undefined, '_set_id should be in the request data');
    const response = await this.axiosInstance.put<IPushSubscriptionResponse>(
      `/pushsubscription/${pushSubscription.pushSubscriptionId}`,
      {
        pushsubscription: pushSubscription,
      } as IPushSubscriptionRequest,
    );
    return response.data?.pushsubscription;
  }

  public async getValues(): Promise<IValue[]> {
    const response =
      await this.axiosInstance.get<IValueListResponse>(`/values`);
    return response.data?.values;
  }

  public async addValue(value: IValue): Promise<IValue> {
    (value as any)._type = "value";
    // TODO Activity Refactor: Who/where should maintained edited time?

    logger.assert(
      (value as any)._rev == undefined,
      "_rev should not be in the request data",
    );
    logger.assert(
      (value as any)._set_id == undefined,
      "_set_id should not be in the request data",
    );

    const response = await this.axiosInstance.post<IValueResponse>(`/values`, {
      value,
    } as IValueRequest);
    return response.data?.value;
  }

  public async deleteValue(value: IValue): Promise<IValue> {
    logger.assert(
      (value as any)._rev != undefined,
      "_rev should be in the request data",
    );
    const response = await this.axiosInstance.delete<IValueResponse>(
      `/value/${value.valueId}`,
      {
        headers: {
          "If-Match": (value as any)._rev,
        },
      },
    );
    return response.data?.value;
  }

  public async updateValue(value: IValue): Promise<IValue> {
    (value as any)._type = "value";
    // TODO Activity Refactor: Who/where should maintained edited time?

    logger.assert(
      (value as any)._rev != undefined,
      "_rev should be in the request data",
    );
    logger.assert(
      (value as any)._set_id != undefined,
      "_set_id should be in the request data",
    );

    const response = await this.axiosInstance.put<IValueResponse>(
      `/value/${value.valueId}`,
      {
        value: value,
      } as IValueRequest,
    );

    return response.data?.value;
  }
}

export const getPatientServiceInstance = (baseUrl: string, patientId: string) =>
  new PatientService(
    [baseUrl, "patient", patientId].map((s) => _.trim(s, "/")).join("/"),
  ) as IPatientService;
