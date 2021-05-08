import { action, computed, makeAutoObservable, observable } from 'mobx';
import { defaultAppConfig } from 'src/services/configs';
import { PromiseQuery, PromiseState } from 'src/services/promiseQuery';
import { useServices } from 'src/services/services';
import { IAppConfig, IUser } from 'src/services/types';
import { AuthStore, IAuthStore } from 'src/stores/AuthStore';
import { IPatientsStore, PatientsStore } from 'src/stores/PatientsStore';
import { IPatientStore } from 'src/stores/PatientStore';
import { IUserStore, UserStore } from 'src/stores/UserStore';

export interface IRootStore {
    // Stores
    userStore: IUserStore;
    authStore: IAuthStore;
    patientsStore: IPatientsStore;

    // App metadata
    appTitle: string;
    appConfig: IAppConfig;

    // UI states
    appState: PromiseState;
    loginState: PromiseState;
    currentPatient: IPatientStore | undefined;

    // Methods
    login: () => void;
    logout: () => void;
    load: () => void;

    setCurrentPatient: (mrn: string) => void;

    getPatientByMRN: (mrn: string | undefined) => IPatientStore | undefined;
}

export class RootStore implements IRootStore {
    // Stores
    public userStore: IUserStore;
    public authStore: IAuthStore;
    public patientsStore: IPatientsStore;

    // App metadata
    public appTitle = 'SCOPE Registry';

    // UI states
    @observable public currentPatient: IPatientStore | undefined = undefined;

    // Promise queries
    private readonly loginQuery: PromiseQuery<IUser | undefined>;
    private readonly configQuery: PromiseQuery<IAppConfig>;

    constructor() {
        this.userStore = new UserStore();
        this.authStore = new AuthStore();
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
        const user = await this.loginQuery.fromPromise(promise);

        if (!!user) {
            this.userStore.updateUser(user.name);
            this.authStore.setAuthToken(user.authToken);
        }
    }

    @action.bound
    public logout() {
        this.loginQuery.state = 'Unknown';

        this.userStore.updateUser('');
        this.authStore.setAuthToken('');
    }

    @action.bound
    public async loadAppConfig() {
        const { appService } = useServices();
        const promise = appService.getAppConfig();
        await this.configQuery.fromPromise(promise);
    }

    @action.bound
    public setCurrentPatient(mrn: string) {
        if (!!mrn) {
            const patient = this.patientsStore.patients.filter((p) => p.MRN == mrn)[0];

            this.currentPatient = patient;
        } else {
            this.currentPatient = undefined;
        }
    }

    public getPatientByMRN(mrn: string | undefined) {
        if (!!mrn) {
            const patient = this.patientsStore.patients.filter((p) => p.MRN == mrn)[0];

            return patient;
        }

        return undefined;
    }
}
