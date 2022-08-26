import axios, { AxiosInstance } from 'axios';
import { IQuoteResponse } from 'shared/serviceTypes';

export interface IAppService {
    getInspirationalQuote(): Promise<string>;
}

class AppService implements IAppService {
    private readonly axiosInstance: AxiosInstance;

    constructor(baseUrl: string) {
        this.axiosInstance = axios.create({
            baseURL: baseUrl,
            timeout: 1000 * 60 * 2,
        });
    }

    public async getInspirationalQuote(): Promise<string> {
        const response = await this.axiosInstance.get<IQuoteResponse>(`/quote`);
        return response.data?.quote;
    }
}

export const getAppServiceInstance = (baseUrl: string) =>
    new AppService(baseUrl) as IAppService;
