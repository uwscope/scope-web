import axios, { AxiosInstance } from 'axios';
import { IAppConfig } from 'shared/types';
import { getQuote } from 'src/services/quotes';

export interface IAppService {
    getAppConfig(): Promise<IAppConfig>;
    getInspirationalQuote(): Promise<string>;
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

    public async getInspirationalQuote(): Promise<string> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.get<string>(`/quote`);
            return response.data;
        } catch (error) {
            const quote = getQuote();
            return await new Promise((resolve) => setTimeout(() => resolve(quote), 1000));
        }
    }
}

export const getAppServiceInstance = (baseUrl: string) => new AppService(baseUrl) as IAppService;
