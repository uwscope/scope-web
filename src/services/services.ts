import { getAuthServiceInstance, IAuthService } from 'src/services/authService';
import { getRegistryServiceInstance, IRegistryService } from 'src/services/registryService';

// TODO: Dummy base url. Read from config
const registryService = getRegistryServiceInstance('http://www.uw.edu');
const authService = getAuthServiceInstance('http://www.uw.edu');

export interface IRootService {
    registryService: IRegistryService;
    authService: IAuthService;
}

export const useServices = () => ({
    registryService,
    authService,
});
