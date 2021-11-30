import axios, { AxiosInstance } from 'axios';
import {
    getFakeActivities,
    getFakeAssessmentLog,
    getFakeLifeareaValues,
    getFakePatientConfig,
    getFakeScheduledItems,
} from 'src/utils/fake';
import {
    IActivity,
    IActivityLog,
    IAssessmentDataPoint,
    ILifeAreaValue,
    IPatientConfig,
    IScheduledTaskItem,
} from './types';

export interface IPatientService {
    getActivities(): Promise<IActivity[]>;
    getTaskItems(): Promise<IScheduledTaskItem[]>;
    getPatientConfig(): Promise<IPatientConfig>;
    getValuesInventory(): Promise<ILifeAreaValue[]>;
    getActivityLogs(): Promise<IActivityLog[]>;
    getAssessmentLogs(): Promise<IAssessmentDataPoint[]>;
    updateActivity(activity: IActivity): Promise<IActivity>;
}

class PatientService implements IPatientService {
    private readonly axiosInstance: AxiosInstance;

    constructor(baseUrl: string) {
        this.axiosInstance = axios.create({
            baseURL: baseUrl,
            timeout: 1000,
        });
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

    public async getTaskItems(): Promise<IScheduledTaskItem[]> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.get<IScheduledTaskItem[]>(`/schedule`);
            return response.data;
        } catch (error) {
            const taskItems = getFakeScheduledItems(5, 7);
            return await new Promise((resolve) => setTimeout(() => resolve(taskItems), 500));
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

    public async getValuesInventory(): Promise<ILifeAreaValue[]> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.get<ILifeAreaValue[]>(`/values`);
            return response.data;
        } catch (error) {
            return await new Promise((resolve) => setTimeout(() => resolve(getFakeLifeareaValues()), 500));
        }
    }

    public async getActivityLogs(): Promise<IActivityLog[]> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.get<IActivityLog[]>(`/activities/log`);
            return response.data;
        } catch (error) {
            return await new Promise((resolve) => setTimeout(() => resolve([]), 500));
        }
    }

    public async getAssessmentLogs(): Promise<IAssessmentDataPoint[]> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.get<IAssessmentDataPoint[]>(`/assessments`);
            return response.data;
        } catch (error) {
            return await new Promise((resolve) => setTimeout(() => resolve([getFakeAssessmentLog()]), 500));
        }
    }

    public async updateActivity(activity: IActivity): Promise<IActivity> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<IActivity>(`/activity/${activity.id}`, activity);
            return response.data;
        } catch (error) {
            return await new Promise((resolve) => setTimeout(() => resolve(activity), 500));
        }
    }
}

export const getPatientServiceInstance = (baseUrl: string) => new PatientService(baseUrl) as IPatientService;
