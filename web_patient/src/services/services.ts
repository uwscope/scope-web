import _ from 'lodash';
import { getAppServiceInstance, IAppService } from 'src/services/appService';
import { getConfigServiceInstance, IConfigService } from 'src/services/configService';
import { getPatientServiceInstance, IPatientService } from 'src/services/patientService';

const combineUrl = (baseUrl: string, path: string) => {
    return [baseUrl, path].map((s) => _.trim(s, '/')).join('/');
};

const appService = getAppServiceInstance(combineUrl(__API__, 'app'));
const patientService = getPatientServiceInstance(combineUrl(__API__, 'patient'));
const configService = getConfigServiceInstance(__API__);

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
