import axios, { AxiosInstance } from 'axios';
import { IUser } from 'shared/types';

export interface IAuthService {
    login(): Promise<IUser>;
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

    public async login(): Promise<IUser> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.get<IUser>('/auth');
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            const user = {
                identityId: 'luke-skywalker-id',
                name: 'Luke Skywalker',
                authToken: 'my token',
            } as IUser;

            return user;
        }
    }
}

export const getAuthServiceInstance = (baseUrl: string) => new AuthService(baseUrl) as IAuthService;
