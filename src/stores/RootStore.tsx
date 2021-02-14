import { action, computed, makeAutoObservable, observable } from 'mobx';
import { PromiseQuery, PromiseState } from 'src/services/promiseQuery';
import { useServices } from 'src/services/services';
import { IUser } from 'src/services/types';
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

    // UI states
    appState: PromiseState;
    loginState: PromiseState;
    currentPatient: IPatientStore | undefined;

    // Methods
    login: () => void;
    logout: () => void;
    load: () => void;

    setCurrentPatient: (mrn: number) => void;
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

    constructor() {
        this.userStore = new UserStore();
        this.authStore = new AuthStore();
        this.patientsStore = new PatientsStore();

        this.loginQuery = new PromiseQuery(undefined, 'loginQuery');

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

    @action.bound
    public async load() {
        await this.login();
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
        this.loginQuery.state == 'Unknown';

        this.userStore.updateUser('');
        this.authStore.setAuthToken('');
    }

    @action.bound
    public setCurrentPatient(mrn: number) {
        if (mrn > 0) {
            const patient = this.patientsStore.patients.filter((p) => p.MRN == mrn)[0];

            this.currentPatient = patient;
        } else {
            this.currentPatient = undefined;
        }
    }
}
