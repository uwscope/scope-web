import { action, makeAutoObservable, observable } from 'mobx';
import { AuthServiceInstance } from 'src/services/authService';
import { RegistryServiceInstance } from 'src/services/registryService';
import { AuthStore, IAuthStore } from './AuthStore';
import { IPatientsStore, IPatientStore, PatientsStore } from './PatientsStore';
import { IUserStore, UserStore } from './UserStore';

export interface IRootStore {
    userStore: IUserStore;
    authStore: IAuthStore;
    patientsStore: IPatientsStore;
    appTitle: string;
    loginStatus: LoginStatus;
    currentPatient: IPatientStore | undefined;
    login: () => void;
    logout: () => void;
    load: () => void;
    setCurrentPatient: (mrn: number) => void;
}

export enum LoginStatus {
    LoggingOut,
    LoggedOut,
    LoggingIn,
    LoggedIn,
}

export class RootStore implements IRootStore {
    public userStore: IUserStore;
    public authStore: IAuthStore;
    public patientsStore: IPatientsStore;
    public appTitle = 'SCOPE Registry';

    @observable public loginStatus = LoginStatus.LoggedOut;
    @observable public currentPatient: IPatientStore | undefined = undefined;

    constructor() {
        this.userStore = new UserStore();
        this.authStore = new AuthStore();
        this.patientsStore = new PatientsStore();

        makeAutoObservable(this);
    }

    @action.bound
    public login() {
        this.loginStatus = LoginStatus.LoggingIn;

        const user = AuthServiceInstance.login();

        this.userStore.updateUser(user.name);
        this.authStore.setAuthToken(user.authToken);

        this.loginStatus = LoginStatus.LoggedIn;
        this.load();
    }

    @action.bound
    public logout() {
        this.loginStatus = LoginStatus.LoggingOut;

        this.userStore.updateUser('');
        this.authStore.setAuthToken('');

        this.loginStatus = LoginStatus.LoggedOut;
    }

    @action.bound
    public load() {
        const patients = RegistryServiceInstance.getPatients();
        this.patientsStore.updatePatients(patients);
        this.patientsStore.filterCareManager(this.userStore.name);
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
