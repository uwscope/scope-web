import axios, { AxiosInstance } from 'axios';
import { defaultAppConfig } from 'src/services/configs';
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
        // TODO: wait for server update:
        const response = await this.axiosInstance.get<IAppConfig>('/config');
        response;
        return defaultAppConfig;
    }
}

export const getAppServiceInstance = (baseUrl: string) => new AppService(baseUrl) as IAppService;
