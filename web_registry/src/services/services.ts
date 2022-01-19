import { getAuthServiceInstance, IAuthService } from 'src/services/authService';
import { getRegistryServiceInstance, IRegistryService } from 'src/services/registryService';

const registryService = getRegistryServiceInstance(CLIENT_CONFIG.flaskBaseUrl);
const authService = getAuthServiceInstance(CLIENT_CONFIG.flaskBaseUrl);

export interface IRootService {
    registryService: IRegistryService;
    authService: IAuthService;
}

export const useServices = () => ({
    registryService,
    authService,
});
