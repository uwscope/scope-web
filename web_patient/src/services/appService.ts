import axios, { AxiosInstance } from 'axios';
import { IQuoteResponse } from 'shared/serviceTypes';
import { IAppConfig } from 'shared/types';

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

        // TODO: fail on purpose since service is not implemented
        response;
        throw new Error('Failure on purpose');
    }

    public async getInspirationalQuote(): Promise<string> {
        const response = await this.axiosInstance.get<IQuoteResponse>(`/quote`);
        return response.data?.quote?.quote;
    }
}

export const getAppServiceInstance = (baseUrl: string) => new AppService(baseUrl) as IAppService;
