import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { handleDates } from 'shared/time';
import { KeyedMap } from 'shared/types';

export interface IServiceBase {
    applyAuth(getToken: () => string | undefined, onUnauthorized?: () => void): void;
}

export class ServiceBase implements IServiceBase {
    protected readonly axiosInstance: AxiosInstance;
    private authRequestInterceptor: number | undefined;
    private authResponseInterceptor: number | undefined;
    private revIds: KeyedMap<string> = {};

    constructor(baseUrl: string) {
        this.axiosInstance = axios.create({
            baseURL: baseUrl,
            timeout: 1000 * 60 * 2,
        });

        const handleDocuments = (body: any) => {
            if (body === null || body === undefined || typeof body !== 'object') {
                return body;
            }

            if (!!body._id && !!body._rev) {
                this.revIds[body._id] = body._rev;
            }

            for (const key of Object.keys(body)) {
                const value = body[key];
                if (typeof value === 'object') {
                    handleDocuments(value);
                }
            }
        };

        const handleResponse = (response: AxiosResponse) => {
            handleDates(response.data);
            handleDocuments(response.data);

            return response;
        };

        const handleError = (error: AxiosError) => {
            if (error.response?.status == 409 && error.response != undefined) {
                handleDates(error.response?.data);
                handleDocuments(error.response?.data);
            }

            throw error;
        };

        const handleRequest = (request: AxiosRequestConfig) => {
            if (request.method?.toLowerCase() === 'put' && request.data) {
                // Get the name of the document. Assume that it is the only field in the data
                const docName = Object.keys(request.data)[0];
                if (!!docName && request.data[docName] && request.data[docName]._id) {
                    if (this.revIds[request.data[docName]._id] != undefined) {
                        request.data[docName]._rev = this.revIds[request.data[docName]._id];
                    }
                    delete request.data[docName]._id;
                }
            }
            return request;
        };

        this.axiosInstance.interceptors.response.use(handleResponse, handleError);

        this.axiosInstance.interceptors.request.use(handleRequest);
    }

    public applyAuth(getToken: () => string | undefined, onUnauthorized?: () => void) {
        // Add auth request interceptor that adds token header
        if (this.authRequestInterceptor) {
            this.axiosInstance.interceptors.request.eject(this.authRequestInterceptor);
        }

        this.authRequestInterceptor = this.axiosInstance.interceptors.request.use((config) => {
            const bearer = `Bearer ${getToken()}`;
            if (!!config.headers) {
                config.headers.Authorization = bearer;
            }

            return config;
        });

        // Add response interceptor that checks for unauthorized access
        if (this.authResponseInterceptor) {
            this.axiosInstance.interceptors.response.eject(this.authResponseInterceptor);
        }

        if (onUnauthorized) {
            this.authResponseInterceptor = this.axiosInstance.interceptors.response.use((response) => {
                if (response.status == 403) {
                    onUnauthorized();
                }

                return response;
            });
        }
    }
}
