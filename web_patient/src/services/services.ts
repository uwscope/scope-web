import _ from 'lodash';
import { getIdentityServiceInstance, IIdentityService } from 'shared/identityService';
import { getAppServiceInstance, IAppService } from 'src/services/appService';
import { getConfigServiceInstance, IConfigService } from 'src/services/configService';

const combineUrl = (baseUrl: string, path: string) => {
    return [baseUrl, path].map((s) => _.trim(s, '/')).join('/');
};

const appService = getAppServiceInstance(combineUrl(CLIENT_CONFIG.flaskBaseUrl, 'app'));
const configService = getConfigServiceInstance(CLIENT_CONFIG.flaskBaseUrl);
const identityService = getIdentityServiceInstance(CLIENT_CONFIG.flaskBaseUrl);

export interface IRootService {
    appService: IAppService;
    configService: IConfigService;
    identityService: IIdentityService;
}

export const useServices = () =>
    ({
        appService,
        configService,
        identityService,
    } as IRootService);
