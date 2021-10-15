import axios, { AxiosInstance } from 'axios';
import { IAppConfig } from './types';

export interface IAppService {
    getAppConfig(): Promise<IAppConfig>;
}

class AppService implements IAppService {
    private readonly axiosInstance: AxiosInstance;

    constructor(baseUrl: string) {
        this.axiosInstance = axios.create({
            baseURL: baseUrl,
            timeout: 1000,
            headers: { 'X-Custom-Header': 'foobar' },
        });
    }

    public async getAppConfig(): Promise<IAppConfig> {
        const response = await this.axiosInstance.get<IAppConfig>('/config');
        return response.data;
    }
}

export const getAppServiceInstance = (baseUrl: string) => new AppService(baseUrl) as IAppService;
