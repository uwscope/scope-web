import {
    getRegistryServiceInstance,
    IRegistryService,
} from 'src/services/registryService';
import { IConfigService, getConfigServiceInstance } from './configService';

const registryService = getRegistryServiceInstance(CLIENT_CONFIG.flaskBaseUrl);
const configService = getConfigServiceInstance(CLIENT_CONFIG.flaskBaseUrl);

export interface IRootService {
    registryService: IRegistryService;
    configService: IConfigService;
}

export const useServices = () => ({
    registryService,
    configService,
});
