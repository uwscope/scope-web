import {
    getRegistryServiceInstance,
    IRegistryService,
} from 'src/services/registryService';

const registryService = getRegistryServiceInstance(CLIENT_CONFIG.flaskBaseUrl);

export interface IRootService {
    registryService: IRegistryService;
}

export const useServices = () => ({
    registryService,
});
