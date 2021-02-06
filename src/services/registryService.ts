import { IPatient } from './types';

export interface IRegistryService {
    // TODO: async/await: Need babel polyfill
    getPatients(): IPatient[]; //Promise<IUser>;
}

class RegistryService implements IRegistryService {
    public getPatients() {
        const patients = [
            {
                firstName: 'Tinker',
                lastName: 'Bell',
            },
            {
                firstName: 'Prince',
                lastName: 'Charming',
            },
        ];

        return patients; //Promise.resolve(user);
    }
}

export const RegistryServiceInstance = new RegistryService() as IRegistryService;
