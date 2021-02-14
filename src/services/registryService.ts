import axios, { AxiosInstance } from 'axios';
import { IPatient } from 'src/services/types';
import { getRandomFakePatients } from 'src/utils/fake';

// TODO: https://github.com/axios/axios#interceptors
export interface IRegistryService {
    getPatients(): Promise<IPatient[]>;
    getPatientData(mrn: number): Promise<IPatient>;
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
}

export const getRegistryServiceInstance = (baseUrl: string) => new RegistryService(baseUrl) as IRegistryService;
