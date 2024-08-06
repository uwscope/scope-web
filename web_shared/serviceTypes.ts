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
  IPatientIdentity,
  IPatientProfile,
  IProviderIdentity,
  IRecentEntryReview,
  ISafetyPlan,
  IScheduledActivity,
  IScheduledAssessment,
  ISession,
  IValue,
  IValuesInventory,
} from "shared/types";

interface IServiceResponse {
  status: number;
  message?: string;
}

export interface IPatientListResponse extends IServiceResponse {
  patients: IPatient[];
}

export interface IPatientResponse extends IServiceResponse {
  patient: IPatient;
}

export interface IPatientProfileRequest {
  profile: IPatientProfile;
}

export interface IPatientProfileResponse extends IServiceResponse {
  profile: IPatientProfile;
}

export interface IClinicalHistoryRequest {
  clinicalhistory: IClinicalHistory;
}

export interface IClinicalHistoryResponse extends IServiceResponse {
  clinicalhistory: IClinicalHistory;
}

export interface IValuesInventoryRequest {
  valuesinventory: IValuesInventory;
}

export interface IValuesInventoryResponse extends IServiceResponse {
  valuesinventory: IValuesInventory;
}

export interface IQuoteResponse extends IServiceResponse {
  quote: string;
}

export interface ISessionListResponse extends IServiceResponse {
  sessions: ISession[];
}

export interface ISessionResponse extends IServiceResponse {
  session: ISession;
}

export interface ISessionRequest {
  session: ISession;
}

export interface ICaseReviewListResponse extends IServiceResponse {
  casereviews: ICaseReview[];
}

export interface ICaseReviewResponse extends IServiceResponse {
  casereview: ICaseReview;
}

export interface ICaseReviewRequest {
  casereview: ICaseReview;
}

export interface IMoodLogListResponse extends IServiceResponse {
  moodlogs: IMoodLog[];
}

export interface IMoodLogResponse extends IServiceResponse {
  moodlog: IMoodLog;
}

export interface IMoodLogRequest {
  moodlog: IMoodLog;
}

export interface IRecentEntryReviewResponse extends IServiceResponse {
  recententryreview: IRecentEntryReview;
}

export interface IRecentEntryReviewRequest {
  recententryreview: IRecentEntryReview;
}

export interface IActivityListResponse extends IServiceResponse {
  activities: IActivity[];
}

export interface IActivityResponse extends IServiceResponse {
  activity: IActivity;
}

export interface IActivityRequest {
  activity: IActivity;
}

export interface IActivityScheduleListResponse extends IServiceResponse {
  activityschedules: IActivitySchedule[];
}

export interface IActivityScheduleResponse extends IServiceResponse {
  activityschedule: IActivitySchedule;
}

export interface IActivityScheduleRequest {
  activityschedule: IActivitySchedule;
}

export interface IProviderIdentityListResponse extends IServiceResponse {
  providers: IProviderIdentity[];
}

export interface IAssessmentListResponse extends IServiceResponse {
  assessments: IAssessment[];
}

export interface IAssessmentResponse extends IServiceResponse {
  assessment: IAssessment;
}

export interface IAssessmentRequest {
  assessment: IAssessment;
}

export interface IAssessmentLogListResponse extends IServiceResponse {
  assessmentlogs: IAssessmentLog[];
}

export interface IAssessmentLogResponse extends IServiceResponse {
  assessmentlog: IAssessmentLog;
}

export interface IAssessmentLogRequest {
  assessmentlog: IAssessmentLog;
}

export interface ISafetyPlanRequest {
  safetyplan: ISafetyPlan;
}

export interface ISafetyPlanResponse extends IServiceResponse {
  safetyplan: ISafetyPlan;
}

export interface IScheduledActivityListResponse extends IServiceResponse {
  scheduledactivities: IScheduledActivity[];
}

export interface IScheduledAssessmentListResponse extends IServiceResponse {
  scheduledassessments: IScheduledAssessment[];
}

export interface IActivityLogListResponse extends IServiceResponse {
  activitylogs: IActivityLog[];
}

export interface IActivityLogResponse extends IServiceResponse {
  activitylog: IActivityLog;
}

export interface IActivityLogRequest {
  activitylog: IActivityLog;
}

export interface IIdentityResponse extends IServiceResponse {
  providerIdentity: IProviderIdentity;
  patientIdentity: IPatientIdentity;
}

export interface IValueRequest {
  value: IValue;
}

export interface IValueResponse extends IServiceResponse {
  value: IValue;
}

export interface IValueListResponse extends IServiceResponse {
  values: IValue[];
}
