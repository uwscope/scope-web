import { AxiosError } from 'axios';
import { action, computed, makeAutoObservable, observable } from 'mobx';

export type PromiseState = 'Unknown' | 'Pending' | 'Fulfilled' | 'Rejected' | 'Conflicted';

export interface IPromiseQueryState {
    readonly state: PromiseState;
    readonly error: boolean;
    readonly pending: boolean;
    readonly done: boolean;
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
    private _conflictFieldName: string | undefined;

    public name: string;

    @observable public value: T | undefined;
    @observable public state: PromiseState = 'Unknown';

    constructor(defaultValue: T | undefined, name: string, conflictFieldName?: string) {
        this._conflictFieldName = conflictFieldName;
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

    public fromPromise(promise: Promise<T>): Promise<T> {
        action(`${this.name} start`, () => {
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
                    action(`${this.name} conflicted`, () => {
                        this.state = 'Conflicted';
                        this.value = this._conflictFieldName
                            ? axiosError.response?.data?.[this._conflictFieldName]
                            : axiosError.response?.data;
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
