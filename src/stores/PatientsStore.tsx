import { action, computed, IObservableArray, makeAutoObservable, observable } from 'mobx';
import { IPatient } from '../services/types';
import { contains, unique } from '../utils/array';

export interface IPatientStore {
    readonly firstName: string;
    readonly lastName: string;
    readonly name: string;
    readonly primaryCareManagerName: string;
    readonly clinicCode: string;
}

export interface IPatientsStore {
    readonly patients: ReadonlyArray<IPatientStore>;
    readonly careManagers: ReadonlyArray<string>;
    readonly clinics: ReadonlyArray<string>;
    readonly selectedCareManager: string;
    readonly selectedClinic: string;
    readonly selectedPatients: ReadonlyArray<IPatientStore>;

    updatePatients: (patients: IPatient[]) => void;
    selectCareManager: (careManager: string) => void;
    selectClinic: (clinic: string) => void;
}

export class PatientStore implements IPatientStore {
    public firstName: string;
    public lastName: string;
    public primaryCareManagerName: string;
    public clinicCode: string;

    constructor(patient: IPatient) {
        makeAutoObservable(this);
        this.firstName = patient.firstName;
        this.lastName = patient.lastName;
        this.primaryCareManagerName = patient.primaryCareManagerName;
        this.clinicCode = patient.clinicCode;
    }

    public get name() {
        return `${this.firstName} ${this.lastName}`;
    }
}

export class PatientsStore implements IPatientsStore {
    @observable public patients: IObservableArray<IPatientStore>;
    @observable public selectedCareManager: string;
    @observable public selectedClinic: string;

    private readonly AllCareManagers = 'All Care Managers';
    private readonly AllClinics = 'All Clinics';

    constructor() {
        this.patients = observable.array([]);
        this.selectedCareManager = this.AllCareManagers;
        this.selectedClinic = this.AllClinics;
        makeAutoObservable(this);
    }

    @computed
    public get careManagers() {
        const cm = unique(this.patients.map((p) => p.primaryCareManagerName)).sort();
        cm.push(this.AllCareManagers);
        return cm;
    }

    @computed
    public get clinics() {
        const cc = unique(this.patients.map((p) => p.clinicCode)).sort();
        cc.push(this.AllClinics);
        return cc;
    }

    @action.bound
    public updatePatients(patients: IPatient[]) {
        this.patients.replace(patients.map((p) => new PatientStore(p)));
    }

    @action.bound
    public selectCareManager(careManager: string) {
        if (contains(this.careManagers, careManager)) {
            this.selectedCareManager = careManager;
        } else {
            this.selectedCareManager = this.AllCareManagers;
        }
    }

    @action.bound
    public selectClinic(clinicCode: string) {
        if (contains(this.clinics, clinicCode)) {
            this.selectedClinic = clinicCode;
        } else {
            this.selectedClinic = this.AllClinics;
        }
    }

    @computed
    public get selectedPatients() {
        var filteredPatients = this.patients.map((p) => p);
        if (this.selectedCareManager != this.AllCareManagers) {
            filteredPatients = filteredPatients.filter((p) => p.primaryCareManagerName == this.selectedCareManager);
        }

        if (this.selectedClinic != this.AllClinics) {
            filteredPatients = filteredPatients.filter((p) => p.clinicCode == this.selectedClinic);
        }

        return filteredPatients;
    }
}
