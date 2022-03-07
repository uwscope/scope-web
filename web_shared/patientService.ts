import { compareAsc } from 'date-fns';
import _ from 'lodash';
import { getLogger } from 'shared/logger';
import { IServiceBase, ServiceBase } from 'shared/serviceBase';
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
    IActivityLogListResponse,
    IActivityLogResponse,
    IActivityLogRequest,
    IScheduledAssessmentListResponse,
} from 'shared/serviceTypes';
import {
    IActivity,
    IActivityLog,
    IAssessment,
    IAssessmentLog,
    ICaseReview,
    IClinicalHistory,
    IMoodLog,
    IPatient,
    IPatientConfig,
    IPatientProfile,
    ISafetyPlan,
    IScheduledActivity,
    IScheduledAssessment,
    ISession,
    IValuesInventory,
} from 'shared/types';
import {
    IActivityListResponse,
    IActivityRequest,
    IActivityResponse,
    IMoodLogListResponse,
    IMoodLogRequest,
    IMoodLogResponse,
} from './serviceTypes';

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
    updateActivity(activity: IActivity): Promise<IActivity>;

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
}

const logger = getLogger('patientService');

class PatientService extends ServiceBase implements IPatientService {
    constructor(baseUrl: string) {
        super(baseUrl);
    }

    public async getPatient(): Promise<IPatient> {
        const response = await this.axiosInstance.get<IPatientResponse>('');
        return response.data?.patient;
    }

    public async getProfile(): Promise<IPatientProfile> {
        const response = await this.axiosInstance.get<IPatientProfileResponse>(`/profile`);
        return response.data?.profile;
    }

    public async updateProfile(profile: IPatientProfile): Promise<IPatientProfile> {
        logger.assert(
            (profile as any)._type === 'profile',
            `invalid _type for patient profile: ${(profile as any)._type}`,
        );

        (profile as any)._type = 'profile';
        if (!!profile.primaryCareManager) {
            (profile.primaryCareManager as any)._type = 'providerIdentity';
        }

        const response = await this.axiosInstance.put<IPatientProfileResponse>(`/profile`, {
            profile,
        } as IPatientProfileRequest);

        return response.data?.profile;
    }

    public async getClinicalHistory(): Promise<IClinicalHistory> {
        const response = await this.axiosInstance.get<IClinicalHistoryResponse>(`/clinicalhistory`);
        return response.data?.clinicalhistory;
    }

    public async updateClinicalHistory(history: IClinicalHistory): Promise<IClinicalHistory> {
        logger.assert(
            (history as any)._type === 'clinicalHistory',
            `invalid _type for patient clinical history: ${(history as any)._type}`,
        );

        (history as any)._type = 'clinicalHistory';
        const response = await this.axiosInstance.put<IClinicalHistoryResponse>(`/clinicalhistory`, {
            clinicalhistory: history,
        } as IClinicalHistoryRequest);

        return response.data?.clinicalhistory;
    }

    public async getValuesInventory(): Promise<IValuesInventory> {
        const response = await this.axiosInstance.get<IValuesInventoryResponse>(`/valuesinventory`);
        const inventory = response.data?.valuesinventory;
        inventory?.values?.sort((a, b) => compareAsc(a.createdDateTime, b.createdDateTime));
        return inventory;
    }

    public async updateValuesInventory(inventory: IValuesInventory): Promise<IValuesInventory> {
        logger.assert(
            (inventory as any)._type === 'valuesInventory',
            `invalid _type for values inventory: ${(inventory as any)._type}`,
        );

        (inventory as any)._type = 'valuesInventory';
        const response = await this.axiosInstance.put<IValuesInventoryResponse>(`/valuesinventory`, {
            valuesinventory: inventory,
        } as IValuesInventoryRequest);
        const updatedInventory = response.data?.valuesinventory;
        updatedInventory?.values?.sort((a, b) => compareAsc(a.createdDateTime, b.createdDateTime));
        return updatedInventory;
    }

    public async getSafetyPlan(): Promise<ISafetyPlan> {
        const response = await this.axiosInstance.get<ISafetyPlanResponse>(`/safetyplan`);
        return response.data?.safetyplan;
    }

    public async updateSafetyPlan(safetyPlan: ISafetyPlan): Promise<ISafetyPlan> {
        logger.assert(
            (safetyPlan as any)._type === 'safetyPlan',
            `invalid _type for values safety plan: ${(safetyPlan as any)._type}`,
        );

        (safetyPlan as any)._type = 'safetyPlan';
        const response = await this.axiosInstance.put<ISafetyPlanResponse>(`/safetyplan`, {
            safetyplan: safetyPlan,
        } as ISafetyPlanRequest);
        return response.data?.safetyplan;
    }

    public async getSessions(): Promise<ISession[]> {
        const response = await this.axiosInstance.get<ISessionListResponse>(`/sessions`);
        return response.data?.sessions;
    }

    public async addSession(session: ISession): Promise<ISession> {
        (session as any)._type = 'session';

        logger.assert((session as any)._rev == undefined, '_rev should not be in the request data');
        logger.assert((session as any)._set_id == undefined, '_set_id should not be in the request data');

        const response = await this.axiosInstance.post<ISessionResponse>(`/sessions`, { session } as ISessionRequest);
        return response.data?.session;
    }

    public async updateSession(session: ISession): Promise<ISession> {
        logger.assert((session as any)._type === 'session', `invalid _type for session: ${(session as any)._type}`);
        logger.assert((session as any)._rev != undefined, '_rev should be in the request data');
        logger.assert((session as any)._set_id != undefined, '_set_id should be in the request data');

        (session as any)._type = 'session';
        const response = await this.axiosInstance.put<ISessionResponse>(`/session/${session.sessionId}`, {
            session,
        } as ISessionRequest);
        return response.data?.session;
    }

    public async getCaseReviews(): Promise<ICaseReview[]> {
        const response = await this.axiosInstance.get<ICaseReviewListResponse>(`/casereviews`);
        return response.data?.casereviews;
    }

    public async addCaseReview(review: ICaseReview): Promise<ICaseReview> {
        (review as any)._type = 'caseReview';
        (review.consultingPsychiatrist as any)._type = 'providerIdentity';

        logger.assert((review as any)._rev == undefined, '_rev should not be in the request data');
        logger.assert((review as any)._set_id == undefined, '_set_id should not be in the request data');

        const response = await this.axiosInstance.post<ICaseReviewResponse>(`/casereviews`, {
            casereview: review,
        } as ICaseReviewRequest);
        return response.data?.casereview;
    }

    public async updateCaseReview(review: ICaseReview): Promise<ICaseReview> {
        (review.consultingPsychiatrist as any)._type = 'providerIdentity';

        logger.assert(
            (review as any)._type === 'caseReview',
            `invalid _type for case review: ${(review as any)._type}`,
        );
        logger.assert((review as any)._rev != undefined, '_rev should be in the request data');
        logger.assert((review as any)._set_id != undefined, '_set_id should be in the request data');

        (review as any)._type = 'caseReview';
        const response = await this.axiosInstance.put<ICaseReviewResponse>(`/casereview/${review.caseReviewId}`, {
            casereview: review,
        } as ICaseReviewRequest);
        return response.data?.casereview;
    }

    public async getScheduledActivities(): Promise<IScheduledActivity[]> {
        const response = await this.axiosInstance.get<IScheduledActivityListResponse>(`/scheduledactivities`);
        return response.data?.scheduledactivities;
    }

    public async getActivities(): Promise<IActivity[]> {
        const response = await this.axiosInstance.get<IActivityListResponse>(`/activities`);
        return response.data?.activities;
    }

    public async addActivity(activity: IActivity): Promise<IActivity> {
        (activity as any)._type = 'activity';

        const response = await this.axiosInstance.post<IActivityResponse>(`/activities`, {
            activity,
        } as IActivityRequest);
        return response.data?.activity;
    }

    public async updateActivity(activity: IActivity): Promise<IActivity> {
        logger.assert((activity as any)._type === 'activity', `invalid _type for activity: ${(activity as any)._type}`);

        (activity as any)._type = 'activity';
        const response = await this.axiosInstance.put<IActivityResponse>(`/activity/${activity.activityId}`, {
            activity,
        } as IActivityRequest);
        return response.data?.activity;
    }

    public async getPatientConfig(): Promise<IPatientConfig> {
        const response = await this.axiosInstance.get<IPatientConfig>(`/summary`);
        return response.data;
    }

    public async getActivityLogs(): Promise<IActivityLog[]> {
        const response = await this.axiosInstance.get<IActivityLogListResponse>(`/activitylogs`);
        return response.data?.activitylogs;
    }

    public async addActivityLog(activityLog: IActivityLog): Promise<IActivityLog> {
        (activityLog as any)._type = 'activityLog';

        const response = await this.axiosInstance.post<IActivityLogResponse>(`/activitylogs`, {
            activitylog: activityLog,
        } as IActivityLogRequest);
        return response.data?.activitylog;
    }

    public async getScheduledAssessments(): Promise<IScheduledAssessment[]> {
        const response = await this.axiosInstance.get<IScheduledAssessmentListResponse>(`/scheduledassessments`);
        return response.data?.scheduledassessments;
    }

    public async getAssessments(): Promise<IAssessment[]> {
        const response = await this.axiosInstance.get<IAssessmentListResponse>(`/assessments`);
        return response.data?.assessments;
    }

    public async updateAssessment(assessment: IAssessment): Promise<IAssessment> {
        logger.assert(
            (assessment as any)._type === 'assessment',
            `invalid _type for assessment: ${(assessment as any)._type}`,
        );

        (assessment as any)._type = 'assessment';
        const response = await this.axiosInstance.put<IAssessmentResponse>(`/assessment/${assessment.assessmentId}`, {
            assessment,
        } as IAssessmentRequest);
        return response.data?.assessment;
    }

    public async getAssessmentLogs(): Promise<IAssessmentLog[]> {
        const response = await this.axiosInstance.get<IAssessmentLogListResponse>(`/assessmentlogs`);
        return response.data?.assessmentlogs;
    }

    public async addAssessmentLog(assessmentLog: IAssessmentLog): Promise<IAssessmentLog> {
        (assessmentLog as any)._type = 'assessmentLog';

        const response = await this.axiosInstance.post<IAssessmentLogResponse>(`/assessmentlogs`, {
            assessmentlog: assessmentLog,
        } as IAssessmentLogRequest);
        return response.data?.assessmentlog;
    }

    public async updateAssessmentLog(assessmentLog: IAssessmentLog): Promise<IAssessmentLog> {
        (assessmentLog as any)._type = 'assessmentLog';
        logger.assert((assessmentLog as any)._rev != undefined, '_rev should be in the request data');
        logger.assert((assessmentLog as any)._set_id != undefined, '_set_id should be in the request data');

        const response = await this.axiosInstance.put<IAssessmentLogResponse>(
            `/assessmentlog/${assessmentLog.assessmentLogId}`,
            {
                assessmentlog: assessmentLog,
            } as IAssessmentLogRequest,
        );

        return response.data?.assessmentlog;
    }

    public async getMoodLogs(): Promise<IMoodLog[]> {
        const response = await this.axiosInstance.get<IMoodLogListResponse>(`/moodlogs`);
        return response.data?.moodlogs;
    }

    public async addMoodLog(moodLog: IMoodLog): Promise<IMoodLog> {
        (moodLog as any)._type = 'moodLog';

        const response = await this.axiosInstance.post<IMoodLogResponse>(`/moodlogs`, {
            moodlog: moodLog,
        } as IMoodLogRequest);
        return response.data?.moodlog;
    }
}

export const getPatientServiceInstance = (baseUrl: string, patientId: string) =>
    new PatientService([baseUrl, 'patient', patientId].map((s) => _.trim(s, '/')).join('/')) as IPatientService;
