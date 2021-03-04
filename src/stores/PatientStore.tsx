import { differenceInYears } from 'date-fns';
import { action, computed, makeAutoObservable, when } from 'mobx';
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
import { IActivity, IAssessment, IAssessmentDataPoint, IPatient, ISession } from 'src/services/types';

export interface IPatientStore extends IPatient {
    readonly name: string;
    readonly age: number;
    readonly state: PromiseState;
    readonly addSessionState: PromiseState;

    getPatientData: () => void;
    updatePatientData: (patient: Partial<IPatient>) => void;
    addSession: (session: Partial<ISession>) => void;
    addAssessmentRecord: (assessment: IAssessmentDataPoint) => void;
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
    public primaryCareManager: string;
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
    private readonly addSessionQuery: PromiseQuery<ISession>;
    private readonly addAssessmentRecordQuery: PromiseQuery<IAssessmentDataPoint>;

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
        this.primaryCareManager = patient.primaryCareManager;
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
        this.addSessionQuery = new PromiseQuery(patient.sessions[0], 'addSession');
        this.addAssessmentRecordQuery = new PromiseQuery<IAssessmentDataPoint>(undefined, 'addAssessmentRecord');

        makeAutoObservable(this);
    }

    @computed get age() {
        return differenceInYears(new Date(), this.birthdate);
    }

    @computed get state() {
        return this.loadPatientDataQuery.state;
    }

    @computed get addSessionState() {
        return this.addSessionQuery.state;
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

    @action.bound
    public async updatePatientData(patient: Partial<IPatient>) {
        const effect = () => {
            const { registryService } = useServices();
            const promise = registryService.updatePatientData(this.MRN, patient);
            this.loadPatientDataQuery.fromPromise(promise).then((patientData) => {
                action(() => {
                    this.setPatientData(patientData);
                })();
            });
        };

        this.runAfterLoad(effect);
    }

    @action.bound
    public async addSession(session: Partial<ISession>) {
        const effect = () => {
            const { registryService } = useServices();
            const promise = registryService.addPatientSession(this.MRN, session);
            this.addSessionQuery.fromPromise(promise).then((session) => {
                action(() => {
                    const addedSession = {
                        ...session,
                        sessionId: this.sessions.length,
                    };
                    this.sessions.push(addedSession);
                })();
            });
        };

        this.runAfterLoad(effect);
    }

    @action.bound
    public addAssessmentRecord(assessmentData: IAssessmentDataPoint) {
        const effect = () => {
            const { registryService } = useServices();
            const promise = registryService.addPatientAssessmentRecord(this.MRN, assessmentData);
            this.addAssessmentRecordQuery.fromPromise(promise).then((data) => {
                action(() => {
                    const phqAssessment = this.assessments.find((a) => a.assessmentType == data.assessmentType);

                    if (phqAssessment) {
                        phqAssessment.data.push(data);
                    }
                })();
            });
        };

        this.runAfterLoad(effect);
    }

    private setPatientData(patient: IPatient) {
        console.log(patient);

        // Medical information
        this.MRN = patient.MRN ?? this.MRN;
        this.firstName = patient.firstName ?? this.firstName;
        this.lastName = patient.lastName ?? this.lastName;
        this.name = `${this.firstName} ${this.lastName}`;
        this.birthdate = patient.birthdate ?? this.birthdate;
        this.sex = patient.sex ?? this.sex;
        this.clinicCode = patient.clinicCode ?? this.clinicCode;
        this.treatmentRegimen = patient.treatmentRegimen ?? this.treatmentPlan;
        this.medicalDiagnosis = patient.medicalDiagnosis ?? this.medicalDiagnosis;

        // Treatment information
        this.primaryCareManager = patient.primaryCareManager ?? this.primaryCareManager;
        this.treatmentStatus = patient.treatmentStatus ?? this.treatmentStatus;
        this.followupSchedule = patient.followupSchedule ?? this.followupSchedule;
        this.discussionFlag = patient.discussionFlag ?? this.discussionFlag;
        this.referral = patient.referral ?? this.referral;
        this.treatmentPlan = patient.treatmentPlan ?? this.treatmentPlan;

        // Psychiatry
        this.psychHistory = patient.psychHistory ?? this.psychHistory;
        this.substanceUse = patient.substanceUse ?? this.substanceUse;
        this.psychMedications = patient.psychMedications ?? this.psychMedications;
        this.psychDiagnosis = patient.psychDiagnosis ?? this.psychDiagnosis;

        // Sessions
        this.sessions = patient.sessions ?? this.sessions;

        // Assessments
        this.assessments = patient.assessments ?? this.assessments;

        // Activities
        this.activities = patient.activities ?? this.activities;
    }

    private runAfterLoad(fn: () => void) {
        if (this.state == 'Pending') {
            when(() => {
                return this.state != 'Pending';
            }, fn);
        } else {
            fn();
        }
    }
}
