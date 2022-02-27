import { AxiosResponse } from 'axios';
import { IServiceBase, ServiceBase } from 'shared/serviceBase';
import { IPatientListResponse, IProviderIdentityListResponse } from 'shared/serviceTypes';
import { IAssessment, IAssessmentLog, IPatient, IProviderIdentity, ISafetyPlan } from 'shared/types';

export interface IRegistryService extends IServiceBase {
    getPatients(): Promise<IPatient[]>;
    addPatient(patient: Partial<IPatient>): Promise<IPatient>;

    getProviders(): Promise<IProviderIdentity[]>;

    updatePatientSafetyPlan(recordId: string, safetyPlan: Partial<ISafetyPlan>): Promise<IPatient>;
    updatePatientAssessment(recordId: string, assessment: Partial<IAssessment>): Promise<IAssessment>;

    addPatientAssessmentLog(recordId: string, assessmentLog: IAssessmentLog): Promise<IAssessmentLog>;
    updatePatientAssessmentLog(recordId: string, assessmentLog: IAssessmentLog): Promise<IAssessmentLog>;
}

class RegistryService extends ServiceBase implements IRegistryService {
    // // Singletons
    // profile
    // clinicalHistory
    // valuesInventory
    // safetyPlan

    // // Arrays
    // sessions
    // caseReviews
    // assessments
    // scheduledAssessments
    // assessmentLogs
    // activities
    // scheduledActivities
    // activityLogs

    constructor(baseUrl: string) {
        super(baseUrl);
    }

    public async getPatients(): Promise<IPatient[]> {
        const response = await this.axiosInstance.get<IPatientListResponse>('/patients');
        return response.data?.patients;
    }

    public async addPatient(patient: Partial<IPatient>): Promise<IPatient> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.post<IPatient, AxiosResponse<IPatient>>('/patients', patient);
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return patient as IPatient;
        }
    }

    public async getProviders(): Promise<IProviderIdentity[]> {
        const response = await this.axiosInstance.get<IProviderIdentityListResponse>('/providers');
        return response.data?.providers;
    }

    public async updatePatientSafetyPlan(recordId: string, safetyPlan: Partial<ISafetyPlan>): Promise<IPatient> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<IPatient>(`/patient/${recordId}`, {
                safetyPlan,
            });
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return { safetyPlan } as IPatient;
        }
    }

    public async updatePatientAssessment(recordId: string, assessment: Partial<IAssessment>): Promise<IAssessment> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<IAssessment>(
                `/patient/${recordId}/assessment/${assessment.assessmentId}`,
                assessment,
            );
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return assessment as IAssessment;
        }
    }

    public async addPatientAssessmentLog(recordId: string, assessmentLog: IAssessmentLog): Promise<IAssessmentLog> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.post<IAssessmentLog>(
                `/patient/${recordId}/assessmentlogs`,
                assessmentLog,
            );
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return assessmentLog;
        }
    }

    public async updatePatientAssessmentLog(recordId: string, assessmentLog: IAssessmentLog): Promise<IAssessmentLog> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<IAssessmentLog>(
                `/patient/${recordId}/assessmentlog/${assessmentLog.logId}`,
                assessmentLog,
            );
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return assessmentLog;
        }
    }
}

export const getRegistryServiceInstance = (baseUrl: string) => new RegistryService(baseUrl) as IRegistryService;
