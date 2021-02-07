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
                primaryCareManagerName: 'Luke Skywalker',
                clinicCode: 'Transplant',
            },
            {
                firstName: 'Prince',
                lastName: 'Charming',
                primaryCareManagerName: 'Luke Skywalker',
                clinicCode: 'Transplant',
            },
        ];

        return patients; //Promise.resolve(user);
    }
}

export const RegistryServiceInstance = new RegistryService() as IRegistryService;
