// TODO: Common between clients
import { AxiosError } from 'axios';
import { action, computed, makeAutoObservable, observable } from 'mobx';

export type PromiseState = 'Unknown' | 'Pending' | 'Fulfilled' | 'Rejected' | 'Conflicted';

export interface IPromiseQueryBase {
    readonly state: PromiseState;
    readonly error: boolean;
    readonly pending: boolean;
    readonly done: boolean;
}

export interface IPromiseQuery<T> extends IPromiseQueryBase {
    readonly value: T | undefined;
    readonly state: PromiseState;
    readonly error: boolean;
    readonly pending: boolean;
    readonly done: boolean;
}

export class PromiseQuery<T> implements IPromiseQuery<T> {
    private _name: string;

    @observable public value: T | undefined;
    @observable public state: PromiseState = 'Unknown';

    constructor(defaultValue: T | undefined, name: string) {
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
        return this.state === 'Fulfilled' || this.error;
    }

    @computed
    public get error() {
        return this.state === 'Rejected' || this.state === 'Conflicted';
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
                const axiosError = error as AxiosError;
                if (axiosError.response?.status == 409) {
                    action(`${this._name} conflicted`, () => {
                        this.state = 'Conflicted';
                        this.value = axiosError.response?.data;
                    })();
                } else {
                    action(`${this._name} rejected`, () => {
                        this.state = 'Rejected';
                    })();
                }

                throw error;
            });
    }
}
