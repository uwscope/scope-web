import axios, { AxiosInstance } from 'axios';
import { IPatientUser } from 'shared/types';

export interface IAuthService {
    login(): Promise<IPatientUser>;
}

class AuthService implements IAuthService {
    private readonly axiosInstance: AxiosInstance;

    constructor(baseUrl: string) {
        this.axiosInstance = axios.create({
            baseURL: baseUrl,
            timeout: 1000,
            headers: { 'X-Custom-Header': 'foobar' },
        });
    }

    public async login(): Promise<IPatientUser> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.get<IPatientUser>('/auth');
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            const user = {
                name: 'Mickey Mouse',
                authToken: 'my token',
                patientId: 'persistent',
            } as IPatientUser;

            return user;
        }
    }
}

export const getAuthServiceInstance = (baseUrl: string) => new AuthService(baseUrl) as IAuthService;
