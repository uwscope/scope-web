import {
    IActivity,
    ICaseReview,
    IClinicalHistory,
    IMoodLog,
    IPatient,
    IPatientProfile,
    ISession,
    IValuesInventory,
} from 'shared/types';

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

export interface ISessionRequest extends IServiceResponse {
    session: ISession;
}

export interface ICaseReviewListResponse extends IServiceResponse {
    casereviews: ICaseReview[];
}

export interface ICaseReviewResponse extends IServiceResponse {
    casereview: ICaseReview;
}

export interface ICaseReviewRequest extends IServiceResponse {
    casereview: ICaseReview;
}

export interface IMoodLogListResponse extends IServiceResponse {
    moodlogs: IMoodLog[];
}

export interface IMoodLogResponse extends IServiceResponse {
    moodlog: IMoodLog;
}

export interface IMoodLogRequest extends IServiceResponse {
    moodlog: IMoodLog;
}

export interface IActivityListResponse extends IServiceResponse {
    activities: IActivity[];
}

export interface IActivityResponse extends IServiceResponse {
    activity: IActivity;
}

export interface IActivityRequest extends IServiceResponse {
    activity: IActivity;
}
