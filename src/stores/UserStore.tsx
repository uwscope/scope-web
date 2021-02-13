import { action, makeAutoObservable, observable } from 'mobx';

export interface IUserStore {
    readonly name: string;
    updateUser: (name: string) => void;
}

export class UserStore implements IUserStore {
    @observable public name = '';

    constructor() {
        makeAutoObservable(this);
    }

    @action
    public updateUser(newName: string) {
        this.name = newName;
    }
}
