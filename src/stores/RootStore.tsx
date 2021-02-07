import { action, makeAutoObservable, observable } from 'mobx';
import { AuthServiceInstance } from '../services/authService';
import { RegistryServiceInstance } from '../services/registryService';
import { AuthStore, IAuthStore } from './AuthStore';
import { IPatientsStore, PatientsStore } from './PatientsStore';
import { IUserStore, UserStore } from './UserStore';

export interface IRootStore {
    userStore: IUserStore;
    authStore: IAuthStore;
    patientsStore: IPatientsStore;
    appTitle: string;
    loginStatus: LoginStatus;
    login: () => void;
    logout: () => void;
    load: () => void;
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

    constructor() {
        makeAutoObservable(this);

        this.userStore = new UserStore();
        this.authStore = new AuthStore();
        this.patientsStore = new PatientsStore();
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
        this.patientsStore.selectCareManager(this.userStore.name);
    }
}
