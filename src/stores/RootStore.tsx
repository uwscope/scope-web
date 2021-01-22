import { action } from "mobx";
import { AuthServiceInstance } from "../services/authService";
import { AuthStore, IAuthStore } from "./AuthStore";
import { IUserStore, UserStore } from "./UserStore";

export interface IRootStore {
    userStore: IUserStore;
    authStore: IAuthStore
    appTitle: string;
    login: () => void;
    logout: () => void;
}


export class RootStore implements IRootStore {

    public userStore: IUserStore;
    public authStore: IAuthStore;
    public appTitle = "SCOPE Registry";

    constructor() {
        // See https://mobx.js.org/enabling-decorators.html
        // makeAutoObservable(this);

        this.userStore = new UserStore();
        this.authStore = new AuthStore();
    }

    @action.bound
    public login() {
        const user = AuthServiceInstance.login();

        this.userStore.updateUser(user.name);
        this.authStore.setAuthToken(user.authToken);
    }

    @action.bound
    public logout() {
        this.userStore.updateUser('');
        this.authStore.setAuthToken('');
    }
}
