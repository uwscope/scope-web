import _ from 'lodash';
import { getAppServiceInstance, IAppService } from 'src/services/appService';
import { getAuthServiceInstance, IAuthService } from 'src/services/authService';
import { getPatientServiceInstance, IPatientService } from 'src/services/patientService';

const combineUrl = (baseUrl: string, path: string) => {
    return [baseUrl, path].map((s) => _.trim(s, '/')).join('/');
};

const authService = getAuthServiceInstance(__API__);
const appService = getAppServiceInstance(combineUrl(__API__, 'app'));
const patientService = getPatientServiceInstance(combineUrl(__API__, 'patient'));

export interface IRootService {
    authService: IAuthService;
    appService: IAppService;
    patientService: IPatientService;
}

export const useServices = () => ({
    authService,
    appService,
    patientService,
});
