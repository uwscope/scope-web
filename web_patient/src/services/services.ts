import _ from 'lodash';
import { getAppServiceInstance, IAppService } from 'src/services/appService';
import { getConfigServiceInstance, IConfigService } from 'src/services/configService';

const combineUrl = (baseUrl: string, path: string) => {
    return [baseUrl, path].map((s) => _.trim(s, '/')).join('/');
};

const appService = getAppServiceInstance(combineUrl(CLIENT_CONFIG.flaskBaseUrl, 'app'));
const configService = getConfigServiceInstance(CLIENT_CONFIG.flaskBaseUrl);

export interface IRootService {
    appService: IAppService;
    configService: IConfigService;
}

export const useServices = () =>
    ({
        appService,
        configService,
    } as IRootService);
