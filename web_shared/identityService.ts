import { AxiosRequestConfig } from 'axios';
import { getLogger } from 'shared/logger';
import { IServiceBase, ServiceBase } from 'shared/serviceBase';
import { IIdentityResponse } from 'shared/serviceTypes';
import { IPatientIdentity, IProviderIdentity } from 'shared/types';

export interface IIdentityService extends IServiceBase {
    getIdentity(token: string): Promise<IPatientIdentity | IProviderIdentity>;
    getPatientIdentity(token: string): Promise<IPatientIdentity>;
    getProviderIdentity(token: string): Promise<IProviderIdentity>;
}

const logger = getLogger('identityService');

class IdentityService extends ServiceBase implements IIdentityService {
    constructor(baseUrl: string) {
        super(baseUrl);
    }

    public async getIdentity(token: string): Promise<IPatientIdentity | IProviderIdentity> {
        const requestConfig = this.getAuthRequestConfig(token);
        const response = await this.axiosInstance.get<IIdentityResponse>('/identities', requestConfig);

        return response.data?.patientIdentity || response.data?.providerIdentity;
    }

    public async getPatientIdentity(token: string): Promise<IPatientIdentity> {
        const requestConfig = this.getAuthRequestConfig(token);
        const response = await this.axiosInstance.get<IIdentityResponse>('/identities/patientIdentity', requestConfig);

        logger.assert(!!response.data?.patientIdentity, 'Did not received expected patient identity');
        return response.data?.patientIdentity;
    }

    public async getProviderIdentity(token: string): Promise<IProviderIdentity> {
        const requestConfig = this.getAuthRequestConfig(token);
        const response = await this.axiosInstance.get<IIdentityResponse>('/identities/providerIdentity', requestConfig);

        logger.assert(!!response.data?.providerIdentity, 'Did not received expected provider identity');
        return response.data?.providerIdentity;
    }

    private getAuthRequestConfig(token: string) {
        return {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        } as AxiosRequestConfig;
    }
}

export const getIdentityServiceInstance = (baseUrl: string) => new IdentityService(baseUrl) as IIdentityService;
