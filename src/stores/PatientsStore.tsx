import { action, computed, IObservableArray, makeAutoObservable, observable } from 'mobx';
import { ClinicCode, DiscussionFlag, FollowupSchedule, TreatmentStatus } from '../services/enums';
import { IPatient } from '../services/types';
import { contains, unique } from '../utils/array';

export interface IPatientStore {
    readonly mrn: number;
    readonly firstName: string;
    readonly lastName: string;
    readonly name: string;
    readonly primaryCareManagerName: string;
    readonly treatmentStatus: TreatmentStatus;
    readonly clinicCode: ClinicCode;
    readonly followupSchedule: FollowupSchedule;
    readonly discussionFlag: DiscussionFlag;
}

export class PatientStore implements IPatientStore {
    public mrn: number;
    public firstName: string;
    public lastName: string;
    public name: string;
    public primaryCareManagerName: string;
    public treatmentStatus: TreatmentStatus;
    public clinicCode: ClinicCode;
    public followupSchedule: FollowupSchedule;
    public discussionFlag: DiscussionFlag;

    constructor(patient: IPatient) {
        this.mrn = patient.MRN;
        this.firstName = patient.firstName;
        this.lastName = patient.lastName;
        this.name = `${this.firstName} ${this.lastName}`;
        this.primaryCareManagerName = patient.primaryCareManagerName;
        this.treatmentStatus = patient.treatmentStatus;
        this.clinicCode = patient.clinicCode;
        this.followupSchedule = patient.followupSchedule;
        this.discussionFlag = patient.discussionFlag;

        makeAutoObservable(this);
    }
}

export type AllClinicCode = 'All Clinics';

export interface IPatientsStore {
    readonly patients: ReadonlyArray<IPatientStore>;
    readonly careManagers: ReadonlyArray<string>;
    readonly clinics: ReadonlyArray<ClinicCode>;
    readonly selectedCareManager: string;
    readonly selectedClinic: ClinicCode | AllClinicCode;
    readonly selectedPatients: ReadonlyArray<IPatientStore>;

    updatePatients: (patients: IPatient[]) => void;
    selectCareManager: (careManager: string) => void;
    selectClinic: (clinic: ClinicCode | AllClinicCode) => void;
}

export class PatientsStore implements IPatientsStore {
    @observable public patients: IObservableArray<IPatientStore>;
    @observable public selectedCareManager: string;
    @observable public selectedClinic: ClinicCode | AllClinicCode;

    private readonly AllCareManagers = 'All Care Managers';

    constructor() {
        this.patients = observable.array([]);
        this.selectedCareManager = this.AllCareManagers;
        this.selectedClinic = 'All Clinics';
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
    public selectClinic(clinicCode: ClinicCode | AllClinicCode) {
        if (contains(this.clinics, clinicCode)) {
            this.selectedClinic = clinicCode;
        } else {
            this.selectedClinic = 'All Clinics';
        }
    }

    @computed
    public get selectedPatients() {
        var filteredPatients = this.patients.map((p) => p);
        if (this.selectedCareManager != this.AllCareManagers) {
            filteredPatients = filteredPatients.filter((p) => p.primaryCareManagerName == this.selectedCareManager);
        }

        if (this.selectedClinic != 'All Clinics') {
            filteredPatients = filteredPatients.filter((p) => p.clinicCode == this.selectedClinic);
        }

        return filteredPatients;
    }
}
