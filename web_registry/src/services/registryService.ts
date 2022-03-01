import { AxiosResponse } from 'axios';
import { IServiceBase, ServiceBase } from 'shared/serviceBase';
import { IPatientListResponse, IProviderIdentityListResponse } from 'shared/serviceTypes';
import { IPatient, IProviderIdentity } from 'shared/types';

export interface IRegistryService extends IServiceBase {
    getPatients(): Promise<IPatient[]>;
    addPatient(patient: Partial<IPatient>): Promise<IPatient>;

    getProviders(): Promise<IProviderIdentity[]>;
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
}

export const getRegistryServiceInstance = (baseUrl: string) => new RegistryService(baseUrl) as IRegistryService;
