import axios, { AxiosInstance } from 'axios';
import { IAppConfig } from 'shared/types';
import { defaultAppConfig } from 'src/services/configs';

export interface IConfigService {
    getServerConfig(): Promise<IAppConfig>;
}

class ConfigService implements IConfigService {
    private readonly axiosInstance: AxiosInstance;

    constructor(baseUrl: string) {
        this.axiosInstance = axios.create({
            baseURL: baseUrl,
            timeout: 15000,
        });
    }

    public async getServerConfig(): Promise<IAppConfig> {
        try {
            await new Promise((resolve) => setTimeout(() => resolve(null), 1000));
            const response = await this.axiosInstance.get<IAppConfig>('app/config');

            return response.data;
        } catch (error) {
            return defaultAppConfig;
        }
    }
}

export const getConfigServiceInstance = (baseUrl: string) => new ConfigService(baseUrl) as IConfigService;
