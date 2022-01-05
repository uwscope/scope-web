import { action, computed, makeAutoObservable } from 'mobx';
import { IAppConfig, IIdentity, IUser } from 'shared/types';
import { defaultAppConfig } from 'src/services/configs';
import { PromiseQuery, PromiseState } from 'src/services/promiseQuery';
import { useServices } from 'src/services/services';
import { IPatientsStore, PatientsStore } from 'src/stores/PatientsStore';
import { IPatientStore } from 'src/stores/PatientStore';

export interface IRootStore {
    // Stores
    currentUserIdentity?: IIdentity;
    userName?: string;
    patientsStore: IPatientsStore;

    // App metadata
    appTitle: string;
    appConfig: IAppConfig;

    // UI states
    appState: PromiseState;
    loginState: PromiseState;

    // Methods
    login: () => void;
    logout: () => void;
    load: () => void;

    getPatientByRecordId: (recordId: string | undefined) => IPatientStore | undefined;
}

export class RootStore implements IRootStore {
    // Stores
    public patientsStore: IPatientsStore;

    // App metadata
    public appTitle = 'SCOPE Registry';

    // Promise queries
    private readonly loginQuery: PromiseQuery<IUser | undefined>;
    private readonly configQuery: PromiseQuery<IAppConfig>;

    constructor() {
        this.patientsStore = new PatientsStore();

        this.loginQuery = new PromiseQuery(undefined, 'loginQuery');
        this.configQuery = new PromiseQuery(defaultAppConfig, 'configQuery');

        makeAutoObservable(this);
    }

    @computed
    public get appState() {
        const { loginState, patientsStore } = this;
        if (loginState == 'Fulfilled' && patientsStore.patients.length > 0) {
            return 'Fulfilled';
        } else if (loginState == 'Pending') {
            return 'Pending';
        }

        return 'Unknown';
    }

    @computed
    public get loginState() {
        return this.loginQuery.state;
    }

    @computed
    public get appConfig() {
        return this.configQuery.value || defaultAppConfig;
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
        await this.login();
        await this.loadAppConfig();
        await this.patientsStore.getPatients();
    }

    @action.bound
    public async login() {
        const { authService } = useServices();
        const promise = authService.login();
        await this.loginQuery.fromPromise(promise);
    }

    @action.bound
    public logout() {
        this.loginQuery.state = 'Unknown';
    }

    @action.bound
    public async loadAppConfig() {
        const { appService } = useServices();
        const promise = appService.getAppConfig();
        await this.configQuery.fromPromise(promise);
    }

    public getPatientByRecordId(recordId: string | undefined) {
        if (!!recordId) {
            const patient = this.patientsStore.patients.filter((p) => p.recordId == recordId)[0];

            return patient;
        }

        return undefined;
    }
}
