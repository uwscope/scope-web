import { differenceInYears } from 'date-fns';
import { action, computed, makeAutoObservable, when } from 'mobx';
import { ClinicCode, DepressionTreatmentStatus, FollowupSchedule, PatientSex } from 'src/services/enums';
import { PromiseQuery, PromiseState } from 'src/services/promiseQuery';
import { useServices } from 'src/services/services';
import {
    CancerTreatmentRegimenFlags,
    DiscussionFlags,
    IActivity,
    IAssessment,
    IAssessmentDataPoint,
    IPatient,
    ISession,
} from 'src/services/types';

export interface IPatientStore extends IPatient {
    readonly name: string;
    readonly age: number;
    readonly state: PromiseState;

    getPatientData: () => void;
    updatePatientData: (patient: Partial<IPatient>) => void;
    updateSession: (session: Partial<ISession>) => void;
    updateAssessment: (assessment: Partial<IAssessment>) => void;
    updateAssessmentRecord: (assessmentData: Partial<IAssessmentDataPoint>) => void;
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

    // Clinical History
    public primaryCancerDiagnosis: string;
    public pastPsychHistory: string;
    public pastSubstanceUse: string;

    // Treatment Information
    public primaryCareManager: string;
    public currentTreatmentRegimen: CancerTreatmentRegimenFlags;
    public currentTreatmentRegimenOther: string;
    public depressionTreatmentStatus: DepressionTreatmentStatus;
    public psychDiagnosis: string;
    public discussionFlag: DiscussionFlags;
    public followupSchedule: FollowupSchedule;

    // TBD
    // public referral: Referral;
    // public treatmentPlan: string;
    // public psychMedications: string;

    // Sessions
    public sessions: ISession[];

    // Assessments
    public assessments: IAssessment[];

    // Activities
    public activities: IActivity[];

    private readonly loadPatientDataQuery: PromiseQuery<IPatient>;
    private readonly updateSessionQuery: PromiseQuery<ISession>;
    private readonly updateAssessmentQuery: PromiseQuery<IAssessment>;
    private readonly updateAssessmentRecordQuery: PromiseQuery<IAssessmentDataPoint>;

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

        // Clinical History
        this.primaryCancerDiagnosis = patient.primaryCancerDiagnosis;
        this.pastPsychHistory = patient.pastPsychHistory;
        this.pastSubstanceUse = patient.pastSubstanceUse;

        // Treatment information
        this.primaryCareManager = patient.primaryCareManager;
        this.currentTreatmentRegimen = patient.currentTreatmentRegimen;
        this.currentTreatmentRegimenOther = patient.currentTreatmentRegimenOther;
        this.depressionTreatmentStatus = patient.depressionTreatmentStatus;
        this.psychDiagnosis = patient.psychDiagnosis;
        this.discussionFlag = patient.discussionFlag;
        this.followupSchedule = patient.followupSchedule;

        // TBD
        // this.referral = patient.referral;
        // this.treatmentPlan = patient.treatmentPlan;
        // this.psychMedications = patient.psychMedications;

        // Sessions
        this.sessions = patient.sessions;

        // Assessments
        this.assessments = patient.assessments;

        // Activities
        this.activities = patient.activities;

        this.loadPatientDataQuery = new PromiseQuery(patient, 'loadPatientData');
        this.updateSessionQuery = new PromiseQuery(patient.sessions[0], 'updateSession');
        this.updateAssessmentQuery = new PromiseQuery<IAssessment>(undefined, 'updateAssessment');
        this.updateAssessmentRecordQuery = new PromiseQuery<IAssessmentDataPoint>(undefined, 'updateAssessmentRecord');

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
    public async updateSession(session: Partial<ISession>) {
        const effect = () => {
            const { registryService } = useServices();
            const promise = registryService.updatePatientSession(this.MRN, session);
            this.updateSessionQuery.fromPromise(promise).then((session) => {
                action(() => {
                    if (!!session.sessionId) {
                        const existing = this.sessions.find((s) => s.sessionId == session.sessionId);

                        if (!!existing) {
                            Object.assign(existing, session);
                            return;
                        }
                    }

                    // TODO: server should return appropriate id
                    const addedSession = {
                        ...session,
                        sessionId: session.sessionId || `session-${this.sessions.length}`,
                    };

                    this.sessions.push(addedSession);
                })();
            });
        };

        this.runAfterLoad(effect);
    }

    @action.bound
    public async updateAssessment(assessment: Partial<IAssessment>) {
        const effect = () => {
            const { registryService } = useServices();
            const promise = registryService.updatePatientAssessment(this.MRN, assessment);
            this.updateAssessmentQuery.fromPromise(promise).then((assessment) => {
                action(() => {
                    if (!!assessment.assessmentId) {
                        const existing = this.assessments.find((a) => a.assessmentId == assessment.assessmentId);

                        if (!!existing) {
                            Object.assign(existing, assessment);
                            return;
                        }
                    }

                    // TODO: server should return appropriate id
                    const addedAssessment = {
                        ...assessment,
                        assessmentId: assessment.assessmentId || assessment.assessmentType,
                    };

                    this.assessments.push(addedAssessment);
                })();
            });
        };

        this.runAfterLoad(effect);
    }

    @action.bound
    public updateAssessmentRecord(assessmentData: Partial<IAssessmentDataPoint>) {
        const effect = () => {
            const { registryService } = useServices();
            const promise = registryService.updatePatientAssessmentRecord(this.MRN, assessmentData);
            this.updateAssessmentRecordQuery.fromPromise(promise).then((data) => {
                action(() => {
                    const assessment = this.assessments.find((a) => a.assessmentType == data.assessmentType);

                    if (!!assessment) {
                        if (!!data.assessmentDataId) {
                            const existing = assessment.data.find((d) => d.assessmentDataId == data.assessmentDataId);

                            if (!!existing) {
                                Object.assign(existing, data);
                                return;
                            }
                        }

                        // TODO: server should return appropriate id
                        const addedAssessmentData = {
                            ...data,
                            assessmentDataId:
                                data.assessmentDataId || `${data.assessmentType}-${assessment?.data.length}`,
                        };

                        assessment.data.push(addedAssessmentData);
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

        // Clinical History
        this.primaryCancerDiagnosis = patient.primaryCancerDiagnosis ?? this.primaryCancerDiagnosis;
        this.pastPsychHistory = patient.pastPsychHistory ?? this.pastPsychHistory;
        this.pastSubstanceUse = patient.pastSubstanceUse ?? this.pastSubstanceUse;

        // Treatment information
        this.primaryCareManager = patient.primaryCareManager ?? this.primaryCareManager;
        this.currentTreatmentRegimen = patient.currentTreatmentRegimen ?? this.currentTreatmentRegimen;
        this.currentTreatmentRegimenOther = patient.currentTreatmentRegimenOther ?? this.currentTreatmentRegimenOther;
        this.depressionTreatmentStatus = patient.depressionTreatmentStatus ?? this.depressionTreatmentStatus;
        this.psychDiagnosis = patient.psychDiagnosis ?? this.psychDiagnosis;
        this.discussionFlag = patient.discussionFlag ?? this.discussionFlag;
        this.followupSchedule = patient.followupSchedule ?? this.followupSchedule;

        // TBD
        // this.referral = patient.referral ?? this.referral;
        // this.treatmentPlan = patient.treatmentPlan ?? this.treatmentPlan;
        // this.psychMedications = patient.psychMedications ?? this.psychMedications;

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
