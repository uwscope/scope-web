import { action, makeAutoObservable, observable } from 'mobx';

export interface IAuthStore {
    readonly authToken: string;
    setAuthToken: (token: string) => void;
}

export class AuthStore implements IAuthStore {
    @observable public authToken = '';

    constructor() {
        makeAutoObservable(this);
    }

    @action setAuthToken(token: string) {
        this.authToken = token;
    }
}
