import { getRandomFakePatients } from '../utils/fake';
import { IPatient } from './types';

export interface IRegistryService {
    // TODO: async/await: Need babel polyfill
    getPatients(): IPatient[]; //Promise<IUser>;
}

class RegistryService implements IRegistryService {
    public getPatients() {
        const patients = getRandomFakePatients();

        return patients; //Promise.resolve(patients);
    }
}

export const RegistryServiceInstance = new RegistryService() as IRegistryService;
