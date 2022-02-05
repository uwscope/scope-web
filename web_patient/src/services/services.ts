import _ from 'lodash';
import { getAppServiceInstance, IAppService } from 'src/services/appService';
import { getConfigServiceInstance, IConfigService } from 'src/services/configService';
import { getPatientServiceInstance, IPatientService } from 'src/services/patientService';

const combineUrl = (baseUrl: string, path: string) => {
    return [baseUrl, path].map((s) => _.trim(s, '/')).join('/');
};

const appService = getAppServiceInstance(combineUrl(CLIENT_CONFIG.flaskBaseUrl, 'app'));
const patientService = getPatientServiceInstance(combineUrl(CLIENT_CONFIG.flaskBaseUrl, 'patient'));
const configService = getConfigServiceInstance(CLIENT_CONFIG.flaskBaseUrl);

export interface IRootService {
    appService: IAppService;
    patientService: IPatientService;
    configService: IConfigService;
}

export const useServices = () => ({
    appService,
    patientService,
    configService,
});
