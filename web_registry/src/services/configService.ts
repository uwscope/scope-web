import axios, { AxiosInstance } from 'axios';
import { IAppConfig } from 'shared/types';

export interface IConfigService {
    getServerConfig(): Promise<IAppConfig>;
}

class ConfigService implements IConfigService {
    private readonly axiosInstance: AxiosInstance;

    constructor(baseUrl: string) {
        this.axiosInstance = axios.create({
            baseURL: baseUrl,
            timeout: 1000 * 60 * 2,
        });
    }

    public async getServerConfig(): Promise<IAppConfig> {
        const response = await this.axiosInstance.get<IAppConfig>('app/config');
        return response.data;
    }
}

export const getConfigServiceInstance = (baseUrl: string) =>
    new ConfigService(baseUrl) as IConfigService;
