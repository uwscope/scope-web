import { trim } from 'lodash';
import { getAppServiceInstance, IAppService } from 'src/services/configService';
import { getRegistryServiceInstance, IRegistryService } from 'src/services/registryService';

const combineUrl = (baseUrl: string, path: string) => {
    return [baseUrl, path].map((s) => trim(s, '/')).join('/');
};

const registryService = getRegistryServiceInstance(__API__);
const appService = getAppServiceInstance(combineUrl(__API__, 'app'));

export interface IRootService {
    registryService: IRegistryService;
    appService: IAppService;
}

export const useServices = () => ({
    registryService,
    appService,
});
