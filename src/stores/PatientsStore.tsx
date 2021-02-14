import { differenceInYears } from 'date-fns';
import { action, computed, IObservableArray, makeAutoObservable, observable } from 'mobx';
import {
    ClinicCode,
    DiscussionFlag,
    FollowupSchedule,
    PatientSex,
    Referral,
    TreatmentRegimen,
    TreatmentStatus,
} from 'src/services/enums';
import { IActivity, IAssessment, IPatient, ISession } from 'src/services/types';
import { contains, unique } from 'src/utils/array';

export interface IPatientStore extends IPatient {
    readonly name: string;
    readonly age: number;
}

export class PatientStore implements IPatientStore {
    // Medical information
    public MRN: number;
    public firstName: string;
    public lastName: string;
    public name: string;
    public birthdate: Date;
    public sex: PatientSex;
    public clinicCode: ClinicCode;
    public treatmentRegimen: TreatmentRegimen;
    public medicalDiagnosis: string;

    // Treatment Information
    public primaryCareManagerName: string;
    public treatmentStatus: TreatmentStatus;
    public followupSchedule: FollowupSchedule;
    public discussionFlag: DiscussionFlag;
    public referral: Referral;
    public treatmentPlan: string;

    // Psychiatry
    public psychHistory: string;
    public substanceUse: string;
    public psychMedications: string;
    public psychDiagnosis: string;

    // Sessions
    public sessions: ISession[];

    // Assessments
    public assessments: IAssessment[];

    // Activities
    public activities: IActivity[];

    constructor(patient: IPatient) {
        // Medical information
        this.MRN = patient.MRN;
        this.firstName = patient.firstName;
        this.lastName = patient.lastName;
        this.name = `${this.firstName} ${this.lastName}`;
        this.birthdate = patient.birthdate;
        this.sex = patient.sex;
        this.clinicCode = patient.clinicCode;
        this.treatmentRegimen = patient.treatmentRegimen;
        this.medicalDiagnosis = patient.medicalDiagnosis;

        // Treatment information
        this.primaryCareManagerName = patient.primaryCareManagerName;
        this.treatmentStatus = patient.treatmentStatus;
        this.followupSchedule = patient.followupSchedule;
        this.discussionFlag = patient.discussionFlag;
        this.referral = patient.referral;
        this.treatmentPlan = patient.treatmentPlan;

        // Psychiatry
        this.psychHistory = patient.psychHistory;
        this.substanceUse = patient.substanceUse;
        this.psychMedications = patient.psychMedications;
        this.psychDiagnosis = patient.psychDiagnosis;

        // Sessions
        this.sessions = patient.sessions;

        // Assessments
        this.assessments = patient.assessments;

        // Activities
        this.activities = patient.activities;

        makeAutoObservable(this);
    }

    @computed get age() {
        return differenceInYears(new Date(), this.birthdate);
    }
}

export type AllClinicCode = 'All Clinics';

export interface IPatientsStore {
    readonly patients: ReadonlyArray<IPatientStore>;
    readonly careManagers: ReadonlyArray<string>;
    readonly clinics: ReadonlyArray<ClinicCode>;
    readonly filteredCareManager: string;
    readonly filteredClinic: ClinicCode | AllClinicCode;
    readonly filteredPatients: ReadonlyArray<IPatientStore>;

    updatePatients: (patients: IPatient[]) => void;
    filterCareManager: (careManager: string) => void;
    filterClinic: (clinic: ClinicCode | AllClinicCode) => void;
}

export class PatientsStore implements IPatientsStore {
    @observable public patients: IObservableArray<IPatientStore>;
    @observable public filteredCareManager: string;
    @observable public filteredClinic: ClinicCode | AllClinicCode;

    private readonly AllCareManagers = 'All Care Managers';

    constructor() {
        this.patients = observable.array([]);
        this.filteredCareManager = this.AllCareManagers;
        this.filteredClinic = 'All Clinics';
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
    public filterCareManager(careManager: string) {
        if (contains(this.careManagers, careManager)) {
            this.filteredCareManager = careManager;
        } else {
            this.filteredCareManager = this.AllCareManagers;
        }
    }

    @action.bound
    public filterClinic(clinicCode: ClinicCode | AllClinicCode) {
        if (contains(this.clinics, clinicCode)) {
            this.filteredClinic = clinicCode;
        } else {
            this.filteredClinic = 'All Clinics';
        }
    }

    @computed
    public get filteredPatients() {
        var filteredPatients = this.patients.map((p) => p);
        if (this.filteredCareManager != this.AllCareManagers) {
            filteredPatients = filteredPatients.filter((p) => p.primaryCareManagerName == this.filteredCareManager);
        }

        if (this.filteredClinic != 'All Clinics') {
            filteredPatients = filteredPatients.filter((p) => p.clinicCode == this.filteredClinic);
        }

        return filteredPatients;
    }
}
