import { action, IObservableArray, makeAutoObservable, observable } from 'mobx';
import { IPatient } from '../services/types';

export interface IPatientStore {
    firstName: string;
    lastName: string;
    name: string;
}

export interface IPatientsStore {
    readonly patients: ReadonlyArray<IPatientStore>;
    updatePatients: (patients: IPatient[]) => void;
}

export class PatientStore implements IPatientStore {
    public firstName: string;
    public lastName: string;

    constructor(patient: IPatient) {
        this.firstName = patient.firstName;
        this.lastName = patient.lastName;
    }

    public get name() {
        return `${this.firstName} ${this.lastName}`;
    }
}

export class PatientsStore implements IPatientsStore {
    @observable public patients: IObservableArray<IPatientStore>;

    constructor() {
        makeAutoObservable(this);
        this.patients = observable.array([]);
    }

    @action.bound updatePatients(patients: IPatient[]) {
        this.patients.replace(patients.map((p) => new PatientStore(p)));
    }
}
