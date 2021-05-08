import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
    AssessmentData,
    IAssessment,
    IAssessmentDataPoint,
    IPatient,
    IPatientList,
    ISession,
} from 'src/services/types';
import { handleDates } from 'src/utils/time';

// TODO: https://github.com/axios/axios#interceptors
export interface IRegistryService {
    getPatients(): Promise<IPatient[]>;
    getPatientData(mrn: string): Promise<IPatient>;
    updatePatientData(mrn: string, patient: Partial<IPatient>): Promise<IPatient>;
    updatePatientSession(mrn: string, session: Partial<ISession>): Promise<ISession>;
    updatePatientAssessment(mrn: string, assessment: Partial<IAssessment>): Promise<IAssessment>;
    updatePatientAssessmentRecord(
        mrn: string,
        assessmentData: Partial<IAssessmentDataPoint>
    ): Promise<IAssessmentDataPoint>;

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

    public async getPatientData(mrn: string): Promise<IPatient> {
        const response = await this.axiosInstance.get<IPatient>(`/patient/${mrn}`);
        return response.data;
    }

    public async updatePatientData(mrn: string, patient: Partial<IPatient>): Promise<IPatient> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<IPatient>(`/patient/${mrn}`, patient);
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return patient as IPatient;
        }
    }

    public async updatePatientSession(mrn: string, session: Partial<ISession>): Promise<ISession> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<ISession>(`/patient/${mrn}/session`, session);
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return session as ISession;
        }
    }

    public async updatePatientAssessment(mrn: string, assessment: Partial<IAssessment>): Promise<IAssessment> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<IAssessment>(`/patient/${mrn}/assessment`, assessment);
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return assessment as IAssessment;
        }
    }

    public async updatePatientAssessmentRecord(
        mrn: string,
        assessmentData: IAssessmentDataPoint
    ): Promise<IAssessmentDataPoint> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<AssessmentData, AxiosResponse<IAssessmentDataPoint>>(
                `/patient/${mrn}/assessment`,
                assessmentData
            );
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return assessmentData;
        }
    }
}

export const getRegistryServiceInstance = (baseUrl: string) => new RegistryService(baseUrl) as IRegistryService;
