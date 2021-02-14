import { differenceInYears } from 'date-fns';
import { action, computed, makeAutoObservable } from 'mobx';
import {
    ClinicCode,
    DiscussionFlag,
    FollowupSchedule,
    PatientSex,
    Referral,
    TreatmentRegimen,
    TreatmentStatus,
} from 'src/services/enums';
import { PromiseQuery, PromiseState } from 'src/services/promiseQuery';
import { useServices } from 'src/services/services';
import { IActivity, IAssessment, IPatient, ISession } from 'src/services/types';

export interface IPatientStore extends IPatient {
    readonly name: string;
    readonly age: number;
    readonly state: PromiseState;

    getPatientData: () => void;
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

    private readonly loadPatientDataQuery: PromiseQuery<IPatient>;

    constructor(patient: IPatient) {
        // Can't refactor due to initialization error
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

        this.loadPatientDataQuery = new PromiseQuery(patient, 'loadPatientData');

        makeAutoObservable(this);
    }

    @computed get age() {
        return differenceInYears(new Date(), this.birthdate);
    }

    @computed get state() {
        return this.loadPatientDataQuery.state;
    }

    @action.bound
    public async getPatientData() {
        if (this.state != 'Pending') {
            const { registryService } = useServices();
            const promise = registryService.getPatientData(this.MRN);
            const patientData = await this.loadPatientDataQuery.fromPromise(promise);
            this.setPatientData(patientData);
        }
    }

    private setPatientData(patient: IPatient) {
        console.log(patient);

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
    }
}
