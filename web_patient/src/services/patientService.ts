import axios, { AxiosInstance } from 'axios';
import { random } from 'lodash';
import { handleDates } from 'shared/time';
import {
    IActivity,
    IActivityLog,
    IAssessmentLog,
    IMoodLog,
    IPatientConfig,
    ISafetyPlan,
    IScheduledActivity,
    IScheduledAssessment,
    IValuesInventory,
} from 'shared/types';
import {
    getFakeActivities,
    getFakeAssessmentLog,
    getFakePatientConfig,
    getFakeSafetyPlan,
    getFakeScheduledActivities,
    getFakeScheduledAssessments,
    getFakeValuesInventory,
} from 'src/utils/fake';

export interface IPatientService {
    applyAuth(authToken: string): void;

    getValuesInventory(): Promise<IValuesInventory>;
    updateValuesInventory(values: IValuesInventory): Promise<IValuesInventory>;

    getSafetyPlan(): Promise<ISafetyPlan>;
    updateSafetyPlan(safetyPlan: ISafetyPlan): Promise<ISafetyPlan>;

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

class PatientService implements IPatientService {
    private readonly axiosInstance: AxiosInstance;
    private authRequestInterceptor: number | undefined;

    constructor(baseUrl: string) {
        console.log(baseUrl);
        this.axiosInstance = axios.create({
            baseURL: baseUrl,
            timeout: 1000,
            headers: { 'X-Custom-Header': 'foobar' },
        });

        this.axiosInstance.interceptors.response.use((response) => {
            handleDates(response.data);
            return response;
        });
    }

    public applyAuth(authToken: string) {
        if (this.authRequestInterceptor) {
            this.axiosInstance.interceptors.request.eject(this.authRequestInterceptor);
        }

        this.authRequestInterceptor = this.axiosInstance.interceptors.request.use(async (config) => {
            const bearer = `Bearer ${authToken}`;
            if (!!config.headers) {
                config.headers.Authorization = bearer;
            }

            return config;
        });
    }

    public async getValuesInventory(): Promise<IValuesInventory> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.get<IValuesInventory>(`/values`);
            return response.data;
        } catch (error) {
            return await new Promise((resolve) => setTimeout(() => resolve(getFakeValuesInventory()), 500));
        }
    }

    public async updateValuesInventory(inventory: IValuesInventory): Promise<IValuesInventory> {
        // Work around since backend doesn't exist
        inventory.lastUpdatedDate = new Date();
        try {
            const response = await this.axiosInstance.put<IValuesInventory>(`/values`, inventory);
            return response.data;
        } catch (error) {
            return await new Promise((resolve) => setTimeout(() => resolve(inventory), 500));
        }
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

export const getPatientServiceInstance = (baseUrl: string) => new PatientService(baseUrl) as IPatientService;
