import { action, computed, makeAutoObservable } from 'mobx';
import { IAppConfig, IIdentity, IUser } from 'shared/types';
import { PromiseQuery } from 'src/services/promiseQuery';
import { useServices } from 'src/services/services';
import { AuthStore, IAuthStore } from 'src/stores/AuthStore';
import { IPatientsStore, PatientsStore } from 'src/stores/PatientsStore';
import { IPatientStore } from 'src/stores/PatientStore';

export interface IRootStore {
    // Stores
    currentUserIdentity?: IIdentity;
    userName?: string;
    patientsStore: IPatientsStore;
    authStore: IAuthStore;

    // App metadata
    appTitle: string;
    appConfig: IAppConfig;

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
    public appConfig: IAppConfig;

    // Promise queries
    private readonly loginQuery: PromiseQuery<IUser | undefined>;

    constructor(serverConfig: IAppConfig) {
        // As more is added to serverConfig, it will become a type and this will be split up
        this.appConfig = serverConfig;
        this.patientsStore = new PatientsStore();
        this.authStore = new AuthStore();

        this.loginQuery = new PromiseQuery(undefined, 'loginQuery');

        makeAutoObservable(this);
    }
    @computed
    public get loginState() {
        return this.loginQuery.state;
    }

    @computed
    public get currentUserIdentity() {
        if (this.loginQuery.state == 'Fulfilled') {
            return this.loginQuery.value;
        } else {
            return undefined;
        }
    }

    @computed
    public get userName() {
        if (this.loginQuery.state == 'Fulfilled') {
            return this.loginQuery.value?.name;
        } else {
            return 'Invalid';
        }
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
