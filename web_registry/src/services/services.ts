import { trim } from 'lodash';
import { getAuthServiceInstance, IAuthService } from 'src/services/authService';
import { getAppServiceInstance, IAppService } from 'src/services/configService';
import { getRegistryServiceInstance, IRegistryService } from 'src/services/registryService';

const combineUrl = (baseUrl: string, path: string) => {
    return [baseUrl, path].map((s) => trim(s, '/')).join('/');
};

const registryService = getRegistryServiceInstance(CLIENT_CONFIG.flaskBaseUrl);
const authService = getAuthServiceInstance(CLIENT_CONFIG.flaskBaseUrl);
const appService = getAppServiceInstance(combineUrl(CLIENT_CONFIG.flaskBaseUrl, 'app'));

export interface IRootService {
    registryService: IRegistryService;
    authService: IAuthService;
    appService: IAppService;
}

export const useServices = () => ({
    registryService,
    authService,
    appService,
});
