import { AxiosError } from 'axios';
import { action, computed, makeAutoObservable, observable } from 'mobx';

export type PromiseState = 'Unknown' | 'Pending' | 'Fulfilled' | 'Rejected' | 'Conflicted';

export interface IPromiseQueryState {
    readonly state: PromiseState;
    readonly error: boolean;
    readonly pending: boolean;
    readonly done: boolean;
    readonly unauthorized: boolean;
    resetState: () => void;
}

export interface IPromiseQuery<T> extends IPromiseQueryState {
    readonly value: T | undefined;
    readonly state: PromiseState;
    readonly error: boolean;
    readonly pending: boolean;
    readonly done: boolean;
    readonly name: string;
}

export class PromiseQuery<T> implements IPromiseQuery<T> {
    public name: string;

    @observable public value: T | undefined;
    @observable public state: PromiseState = 'Unknown';
    @observable public unauthorized: boolean = false;

    constructor(defaultValue: T | undefined, name: string) {
        this.value = defaultValue;
        this.name = name;

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

    public fromPromise(promise: Promise<T>, onConflict?: (responseData?: any) => T): Promise<T> {
        action(`${this.name} start`, () => {
            this.state = 'Pending';
            this.unauthorized = false;
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
                    action(`${this.name} conflicted`, () => {
                        this.state = 'Conflicted';

                        if (onConflict) {
                            this.value = onConflict(axiosError.response?.data);
                        }
                    })();
                } else if (axiosError.response?.status == 403) {
                    action(`${this.name} unauthorized`, () => {
                        this.state = 'Rejected';
                        this.unauthorized = true;
                    })();
                } else {
                    action(`${this.name} rejected`, () => {
                        this.state = 'Rejected';
                    })();
                }

                throw error;
            });
    }

    public resetState() {
        this.state = this.value != undefined ? 'Fulfilled' : 'Unknown';
    }
}
