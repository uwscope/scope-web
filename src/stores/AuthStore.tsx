import { action, computed, makeAutoObservable, observable } from "mobx";

export interface IAuthStore {
    readonly authToken: string;
    readonly loggedIn: boolean;
    setAuthToken: (token: string) => void;
}

export class AuthStore implements IAuthStore {

    @observable public authToken = '';

    constructor() {
        makeAutoObservable(this);
    }

    @computed public get loggedIn() {
        return !!this.authToken;
    }

    @action setAuthToken(token: string) {
        this.authToken = token;
    }
}
