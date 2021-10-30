import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
    AssessmentData,
    IAssessment,
    IAssessmentDataPoint,
    ICaseReview,
    IPatient,
    IPatientList,
    IPatientProfile,
    ISession,
    IValuesInventory,
} from 'src/services/types';
import { handleDates } from 'src/utils/time';

// TODO: https://github.com/axios/axios#interceptors
export interface IRegistryService {
    getPatients(): Promise<IPatient[]>;
    getPatientData(recordId: string): Promise<IPatient>;
    updatePatientData(recordId: string, patient: Partial<IPatient>): Promise<IPatient>;
    updatePatientSession(recordId: string, session: Partial<ISession>): Promise<ISession>;
    updatePatientCaseReview(recordId: string, caseReview: Partial<ICaseReview>): Promise<ICaseReview>;
    updatePatientAssessment(recordId: string, assessment: Partial<IAssessment>): Promise<IAssessment>;
    updatePatientAssessmentRecord(
        recordId: string,
        assessmentData: Partial<IAssessmentDataPoint>
    ): Promise<IAssessmentDataPoint>;
    updateValuesInventory(recordId: string, valuesInventory: Partial<IValuesInventory>): Promise<IValuesInventory>;
    addPatient(patient: Partial<IPatientProfile>): Promise<IPatient>;

    // TODO:
    // Get assessment questionnaires from server
    // Add patient
    // Separate add from update?
}

class RegistryService implements IRegistryService {
    private readonly axiosInstance: AxiosInstance;

    constructor(baseUrl: string) {
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

    public async getPatients(): Promise<IPatient[]> {
        const response = await this.axiosInstance.get<IPatientList>('/patients');
        return response.data && response.data.patients;
    }

    public async getPatientData(recordId: string): Promise<IPatient> {
        const response = await this.axiosInstance.get<IPatient>(`/patient/${recordId}`);
        return response.data;
    }

    public async updatePatientData(recordId: string, patient: Partial<IPatient>): Promise<IPatient> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<IPatient>(`/patient/${recordId}`, patient);
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return patient as IPatient;
        }
    }

    public async updatePatientSession(recordId: string, session: Partial<ISession>): Promise<ISession> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<ISession>(`/patient/${recordId}/session`, session);
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return session as ISession;
        }
    }

    public async updatePatientCaseReview(recordId: string, caseReview: Partial<ICaseReview>): Promise<ICaseReview> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<ICaseReview>(`/patient/${recordId}/review`, caseReview);
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return caseReview as ICaseReview;
        }
    }

    public async updatePatientAssessment(recordId: string, assessment: Partial<IAssessment>): Promise<IAssessment> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<IAssessment>(`/patient/${recordId}/assessment`, assessment);
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return assessment as IAssessment;
        }
    }

    public async updatePatientAssessmentRecord(
        recordId: string,
        assessmentData: IAssessmentDataPoint
    ): Promise<IAssessmentDataPoint> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<AssessmentData, AxiosResponse<IAssessmentDataPoint>>(
                `/patient/${recordId}/assessment`,
                assessmentData
            );
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return assessmentData;
        }
    }

    public async updateValuesInventory(
        recordId: string,
        valuesInventory: Partial<IValuesInventory>
    ): Promise<IValuesInventory> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<IValuesInventory, AxiosResponse<IValuesInventory>>(
                `/patient/${recordId}/values`,
                valuesInventory
            );
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            valuesInventory.assignedDate = new Date();
            return valuesInventory as IValuesInventory;
        }
    }

    public async addPatient(patient: Partial<IPatientProfile>): Promise<IPatient> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<IPatientProfile, AxiosResponse<IPatient>>(
                '/patient',
                patient
            );
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return patient as IPatient;
        }
    }
}

export const getRegistryServiceInstance = (baseUrl: string) => new RegistryService(baseUrl) as IRegistryService;
