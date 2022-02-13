import axios, { AxiosInstance } from 'axios';
import { IAppConfig } from 'shared/types';
import { defaultAppContentConfig } from 'src/services/configs';

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
        await new Promise((resolve) => setTimeout(() => resolve(null), 3000));
        const response = await this.axiosInstance.get<IAppConfig>('app/config');

        // TODO: Jina needs to reconcile configs.ts with server_flask/app_config
        //       Then we can remove this.
        response.data.content = defaultAppContentConfig;

        return response.data;
    }
}

export const getConfigServiceInstance = (baseUrl: string) => new ConfigService(baseUrl) as IConfigService;
