import { compareAsc } from 'date-fns';
import _, { random } from 'lodash';
import {
    getFakeActivities,
    getFakeAssessmentLog,
    getFakePatientConfig,
    getFakeSafetyPlan,
    getFakeScheduledActivities,
    getFakeScheduledAssessments,
} from 'shared/fake';
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
} from 'shared/serviceTypes';
import {
    IActivity,
    IActivityLog,
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

export interface IPatientService extends IServiceBase {
    applyAuth(authToken: string): void;

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

    // TODO: Move get/update safety plan from registryService

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

    getPatientConfig(): Promise<IPatientConfig>;

    getActivityLogs(): Promise<IActivityLog[]>;
    addActivityLog(activityLog: IActivityLog): Promise<IActivityLog>;

    getScheduledAssessments(): Promise<IScheduledAssessment[]>;
    getAssessmentLogs(): Promise<IAssessmentLog[]>;
    addAssessmentLog(assessmentLog: IAssessmentLog): Promise<IAssessmentLog>;

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
            (profile as any)._type === 'patientProfile',
            `invalid _type for patient profile: ${(profile as any)._type}`,
        );

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
        const response = await this.axiosInstance.put<IValuesInventoryResponse>(`/valuesinventory`, {
            valuesinventory: inventory,
        } as IValuesInventoryRequest);
        const updatedInventory = response.data?.valuesinventory;
        updatedInventory?.values?.sort((a, b) => compareAsc(a.createdDateTime, b.createdDateTime));
        return updatedInventory;
    }

    public async getSafetyPlan(): Promise<ISafetyPlan> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.get<ISafetyPlan>(`/safety`);
            return response.data;
        } catch (error) {
            return await new Promise((resolve) => setTimeout(() => resolve(getFakeSafetyPlan()), 500));
        }
    }

    public async updateSafetyPlan(safetyPlan: ISafetyPlan): Promise<ISafetyPlan> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<ISafetyPlan>(`/safety`, safetyPlan);
            return response.data;
        } catch (error) {
            return await new Promise((resolve) => setTimeout(() => resolve(safetyPlan), 500));
        }
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
        (review.consultingPsychiatrist as any)._type = 'identity';

        logger.assert((review as any)._rev == undefined, '_rev should not be in the request data');
        logger.assert((review as any)._set_id == undefined, '_set_id should not be in the request data');

        const response = await this.axiosInstance.post<ICaseReviewResponse>(`/casereviews`, {
            casereview: review,
        } as ICaseReviewRequest);
        return response.data?.casereview;
    }

    public async updateCaseReview(review: ICaseReview): Promise<ICaseReview> {
        (review.consultingPsychiatrist as any)._type = 'identity';

        logger.assert(
            (review as any)._type === 'caseReview',
            `invalid _type for case review: ${(review as any)._type}`,
        );
        logger.assert((review as any)._rev != undefined, '_rev should be in the request data');
        logger.assert((review as any)._set_id != undefined, '_set_id should be in the request data');

        const response = await this.axiosInstance.put<ICaseReviewResponse>(`/casereview/${review.caseReviewId}`, {
            casereview: review,
        } as ICaseReviewRequest);
        return response.data?.casereview;
    }

    public async getScheduledActivities(): Promise<IScheduledActivity[]> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.get<IScheduledActivity[]>(`/activities/schedule`);
            return response.data;
        } catch (error) {
            const taskItems = getFakeScheduledActivities(5, 7);
            return await new Promise((resolve) => setTimeout(() => resolve(taskItems), 500));
        }
    }

    public async getActivities(): Promise<IActivity[]> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.get<IActivity[]>(`/activities`);
            return response.data;
        } catch (error) {
            const activities = getFakeActivities();
            return await new Promise((resolve) => setTimeout(() => resolve(activities), 500));
        }
    }

    public async addActivity(activity: IActivity): Promise<IActivity> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.post<IActivity>(`/activities`, activity);
            return response.data;
        } catch (error) {
            return await new Promise((resolve) => setTimeout(() => resolve(activity), 500));
        }
    }

    public async updateActivity(activity: IActivity): Promise<IActivity> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<IActivity>(`/activity/${activity.activityId}`, activity);
            return response.data;
        } catch (error) {
            return await new Promise((resolve) => setTimeout(() => resolve(activity), 500));
        }
    }

    public async getPatientConfig(): Promise<IPatientConfig> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.get<IPatientConfig>(`/config`);
            return response.data;
        } catch (error) {
            const config = getFakePatientConfig();
            return await new Promise((resolve) => setTimeout(() => resolve(config), 500));
        }
    }

    public async getActivityLogs(): Promise<IActivityLog[]> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.get<IActivityLog[]>(`/activitylogs`);
            return response.data;
        } catch (error) {
            return await new Promise((resolve) => setTimeout(() => resolve([]), 500));
        }
    }

    public async addActivityLog(activityLog: IActivityLog): Promise<IActivityLog> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.post<IActivityLog>(`/activitylogs`, activityLog);
            return response.data;
        } catch (error) {
            activityLog.logId = random(100000).toString();
            activityLog.recordedDate = new Date();
            return await new Promise((resolve) => setTimeout(() => resolve(activityLog), 500));
        }
    }

    public async getScheduledAssessments(): Promise<IScheduledAssessment[]> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.get<IScheduledAssessment[]>(`/assessments/schedule`);
            return response.data;
        } catch (error) {
            const taskItems = getFakeScheduledAssessments();
            return await new Promise((resolve) => setTimeout(() => resolve(taskItems), 500));
        }
    }

    public async getAssessmentLogs(): Promise<IAssessmentLog[]> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.get<IAssessmentLog[]>(`/assessmentlogs`);
            return response.data;
        } catch (error) {
            return await new Promise((resolve) => setTimeout(() => resolve([getFakeAssessmentLog()]), 500));
        }
    }

    public async addAssessmentLog(assessmentLog: IAssessmentLog): Promise<IAssessmentLog> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.post<IAssessmentLog>(`/assessmentlogs`, assessmentLog);
            return response.data;
        } catch (error) {
            assessmentLog.logId = random(100000).toString();
            assessmentLog.recordedDate = new Date();
            return await new Promise((resolve) => setTimeout(() => resolve(assessmentLog), 500));
        }
    }

    public async getMoodLogs(): Promise<IMoodLog[]> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.get<IMoodLog[]>(`/moodlogs`);
            return response.data;
        } catch (error) {
            return await new Promise((resolve) => setTimeout(() => resolve([]), 500));
        }
    }

    public async addMoodLog(moodLog: IMoodLog): Promise<IMoodLog> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.post<IMoodLog>(`/moodlogs`, moodLog);
            return response.data;
        } catch (error) {
            moodLog.logId = random(100000).toString();
            moodLog.recordedDate = new Date();
            return await new Promise((resolve) => setTimeout(() => resolve(moodLog), 500));
        }
    }
}

export const getPatientServiceInstance = (baseUrl: string, patientId: string) =>
    new PatientService([baseUrl, 'patient', patientId].map((s) => _.trim(s, '/')).join('/')) as IPatientService;
