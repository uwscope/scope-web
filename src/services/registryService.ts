import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { AssessmentData, IAssessmentDataPoint, IPatient, ISession } from 'src/services/types';
import { getRandomFakePatients } from 'src/utils/fake';

// TODO: https://github.com/axios/axios#interceptors
export interface IRegistryService {
    getPatients(): Promise<IPatient[]>;
    getPatientData(mrn: number): Promise<IPatient>;
    updatePatientData(mrn: number, patient: Partial<IPatient>): Promise<IPatient>;
    addPatientSession(mrn: number, session: Partial<ISession>): Promise<ISession>;
    addPatientPHQ9Record(mrn: number, phq9: AssessmentData): Promise<IAssessmentDataPoint>;
}

class RegistryService implements IRegistryService {
    private readonly axiosInstance: AxiosInstance;

    constructor(baseUrl: string) {
        this.axiosInstance = axios.create({
            baseURL: baseUrl,
            timeout: 1000,
            headers: { 'X-Custom-Header': 'foobar' },
        });
    }

    public async getPatients(): Promise<IPatient[]> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.get<IPatient[]>('/patients');
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return getRandomFakePatients();
        }
    }

    public async getPatientData(mrn: number): Promise<IPatient> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.get<IPatient>(`/patient/${mrn}`);
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return getRandomFakePatients()[0];
        }
    }

    public async updatePatientData(mrn: number, patient: Partial<IPatient>): Promise<IPatient> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<IPatient>(`/patient/${mrn}`, patient);
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return patient as IPatient;
        }
    }

    public async addPatientSession(mrn: number, session: Partial<ISession>): Promise<ISession> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<ISession>(`/patient/${mrn}/session`, session);
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return session as ISession;
        }
    }

    public async addPatientPHQ9Record(mrn: number, phq9: AssessmentData): Promise<IAssessmentDataPoint> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<AssessmentData, AxiosResponse<IAssessmentDataPoint>>(
                `/patient/${mrn}/phq9`,
                phq9
            );
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return {
                date: new Date(),
                pointValues: phq9,
                comment: 'added my care manager',
            } as IAssessmentDataPoint;
        }
    }
}

export const getRegistryServiceInstance = (baseUrl: string) => new RegistryService(baseUrl) as IRegistryService;
