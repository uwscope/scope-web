import { action, makeAutoObservable } from 'mobx';
import { IAppConfig, IAppContentConfig } from 'shared/types';
import { AuthStore, IAuthStore } from 'src/stores/AuthStore';
import { IPatientsStore, PatientsStore } from 'src/stores/PatientsStore';
import { IPatientStore } from 'src/stores/PatientStore';

export interface IRootStore {
    // Stores
    patientsStore: IPatientsStore;
    authStore: IAuthStore;

    // App metadata
    appTitle: string;
    appContentConfig: IAppContentConfig;

    // UI states

    // Methods
    load: () => void;

    getPatientByRecordId: (
        recordId: string | undefined
    ) => IPatientStore | undefined;
}

export class RootStore implements IRootStore {
    // Stores
    public patientsStore: IPatientsStore;
    public authStore: IAuthStore;

    // App metadata
    public appTitle = 'SCOPE Registry';
    public appContentConfig: IAppContentConfig;

    constructor(serverConfig: IAppConfig) {
        // As more is added to serverConfig, it will become a type and this will be split up
        // James 2/10: When added, the IAppAuthConfig would be passed into the AuthStore?
        this.appContentConfig = serverConfig.content;
        this.patientsStore = new PatientsStore();
        this.authStore = new AuthStore(serverConfig.auth);

        makeAutoObservable(this);
    }

    @action.bound
    public async load() {
        await this.patientsStore.getPatients();
    }

    public getPatientByRecordId(recordId: string | undefined) {
        if (!!recordId) {
            const patient = this.patientsStore.patients.filter(
                (p) => p.recordId == recordId
            )[0];

            return patient;
        }

        return undefined;
    }
}
