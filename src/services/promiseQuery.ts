import { action, computed, makeAutoObservable, observable } from 'mobx';

export type PromiseState = 'Unknown' | 'Pending' | 'Fulfilled' | 'Rejected';

export interface IPromiseQuery<T> {
    readonly value: T;
    readonly state: PromiseState;
    readonly error: boolean;
    readonly pending: boolean;
    readonly done: boolean;
}

export class PromiseQuery<T> implements IPromiseQuery<T> {
    private _name: string;

    @observable public value: T;
    @observable public state: PromiseState = 'Unknown';

    constructor(defaultValue: T, name: string) {
        this.value = defaultValue;
        this._name = name;

        makeAutoObservable(this);
    }

    @computed
    public get pending() {
        return this.state === 'Pending';
    }

    @computed
    public get done() {
        return this.state === 'Fulfilled' || this.state === 'Rejected';
    }

    @computed
    public get error() {
        return this.state === 'Rejected';
    }

    public fromPromise(promise: Promise<T>): Promise<T> {
        action(`${this._name} start`, () => {
            this.state = 'Pending';
        })();

        return promise
            .then((value) => {
                action(() => {
                    this.state = 'Fulfilled';
                    this.value = value;
                })();
                return value;
            })
            .catch((error) => {
                action(`${this._name} rejected`, () => {
                    this.state = 'Rejected';
                })();
                throw error;
            });
    }
}
