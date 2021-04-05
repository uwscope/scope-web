import { getAuthServiceInstance, IAuthService } from 'src/services/authService';
import { getRegistryServiceInstance, IRegistryService } from 'src/services/registryService';

const registryService = getRegistryServiceInstance(__API__);
const authService = getAuthServiceInstance(__API__);

export interface IRootService {
    registryService: IRegistryService;
    authService: IAuthService;
}

export const useServices = () => ({
    registryService,
    authService,
});
