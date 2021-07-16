import { differenceInYears } from 'date-fns';
import { action, computed, makeAutoObservable, when } from 'mobx';
import {
    ClinicCode,
    DepressionTreatmentStatus,
    FollowupSchedule,
    PatientGender,
    PatientPronoun,
    PatientRaceEthnicity,
    PatientSex,
} from 'src/services/enums';
import { PromiseQuery, PromiseState } from 'src/services/promiseQuery';
import { useServices } from 'src/services/services';
import {
    CancerTreatmentRegimenFlags,
    DiscussionFlags,
    IActivity,
    IAssessment,
    IAssessmentDataPoint,
    ICaseReview,
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
    updateCaseReview: (caseReview: Partial<ICaseReview>) => void;
    updateAssessment: (assessment: Partial<IAssessment>) => void;
    updateAssessmentRecord: (assessmentData: Partial<IAssessmentDataPoint>) => void;
}

export class PatientStore implements IPatientStore {
    // IPatientProfile
    public recordId: string;
    public name: string;
    public MRN: string;
    public clinicCode: ClinicCode;
    public depressionTreatmentStatus: DepressionTreatmentStatus;
    public birthdate: Date;
    public sex: PatientSex;
    public gender: PatientGender;
    public pronoun: PatientPronoun;
    public race: PatientRaceEthnicity;
    public primaryOncologyProvider: string;
    public primaryCareManager: string;

    // Clinical History
    public primaryCancerDiagnosis: string;
    public pastPsychHistory: string;
    public pastSubstanceUse: string;

    // Treatment Information
    // public primaryCareManager: string;
    public currentTreatmentRegimen: CancerTreatmentRegimenFlags;
    public currentTreatmentRegimenOther: string;
    public currentTreatmentRegimenNotes: string;
    public psychDiagnosis: string;
    public discussionFlag: DiscussionFlags;
    public followupSchedule: FollowupSchedule;

    // TBD
    // public referral: Referral;
    // public treatmentPlan: string;
    // public psychMedications: string;

    // Sessions
    public sessions: ISession[] = [];
    public caseReviews: ICaseReview[] = [];

    // Assessments
    public assessments: IAssessment[] = [];

    // Activities
    public activities: IActivity[] = [];

    private readonly loadPatientDataQuery: PromiseQuery<IPatient>;
    private readonly updateSessionQuery: PromiseQuery<ISession>;
    private readonly updateCaseReviewQuery: PromiseQuery<ICaseReview>;
    private readonly updateAssessmentQuery: PromiseQuery<IAssessment>;
    private readonly updateAssessmentRecordQuery: PromiseQuery<IAssessmentDataPoint>;

    constructor(patient: IPatient) {
        // IPatientProfile
        this.recordId = patient.recordId;
        this.name = patient.name;
        this.MRN = patient.MRN;
        this.clinicCode = patient.clinicCode;
        this.depressionTreatmentStatus = patient.depressionTreatmentStatus;
        this.birthdate = patient.birthdate;
        this.sex = patient.sex;
        this.gender = patient.gender;
        this.pronoun = patient.pronoun;
        this.race = patient.race;
        this.primaryOncologyProvider = patient.primaryOncologyProvider;
        this.primaryCareManager = patient.primaryCareManager;

        // Clinical History
        this.primaryCancerDiagnosis = patient.primaryCancerDiagnosis;
        this.pastPsychHistory = patient.pastPsychHistory;
        this.pastSubstanceUse = patient.pastSubstanceUse;

        // Treatment information
        this.currentTreatmentRegimen = patient.currentTreatmentRegimen;
        this.currentTreatmentRegimenOther = patient.currentTreatmentRegimenOther;
        this.currentTreatmentRegimenNotes = patient.currentTreatmentRegimenNotes;
        this.psychDiagnosis = patient.psychDiagnosis;
        this.discussionFlag = patient.discussionFlag;
        this.followupSchedule = patient.followupSchedule;

        // Sessions
        this.sessions = patient.sessions || [];
        this.caseReviews = patient.caseReviews || [];

        // Assessments
        this.assessments = patient.assessments || [];

        // Activities
        this.activities = patient.activities || [];

        this.loadPatientDataQuery = new PromiseQuery(patient, 'loadPatientData');
        this.updateSessionQuery = new PromiseQuery<ISession>(undefined, 'updateSession');
        this.updateCaseReviewQuery = new PromiseQuery<ICaseReview>(undefined, 'updateCaseReview');
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
            const promise = registryService.getPatientData(this.recordId);
            const patientData = await this.loadPatientDataQuery.fromPromise(promise);
            this.setPatientData(patientData);
        }
    }

    @action.bound
    public async updatePatientData(patient: Partial<IPatient>) {
        const effect = () => {
            const { registryService } = useServices();
            const promise = registryService.updatePatientData(this.recordId, patient);
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
            const promise = registryService.updatePatientSession(this.recordId, session);
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
    public async updateCaseReview(caseReview: Partial<ICaseReview>) {
        const effect = () => {
            const { registryService } = useServices();
            const promise = registryService.updatePatientCaseReview(this.recordId, caseReview);
            this.updateCaseReviewQuery.fromPromise(promise).then((caseReview) => {
                action(() => {
                    if (!!caseReview.reviewNote) {
                        const existing = this.caseReviews.find((s) => s.reviewId == caseReview.reviewId);

                        if (!!existing) {
                            Object.assign(existing, caseReview);
                            return;
                        }
                    }

                    // TODO: server should return appropriate id
                    const addedCaseReview = {
                        ...caseReview,
                        reviewId: caseReview.reviewId || `review-${this.caseReviews.length}`,
                    };

                    this.caseReviews.push(addedCaseReview);
                })();
            });
        };

        this.runAfterLoad(effect);
    }

    @action.bound
    public async updateAssessment(assessment: Partial<IAssessment>) {
        const effect = () => {
            const { registryService } = useServices();
            const promise = registryService.updatePatientAssessment(this.recordId, assessment);
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
            const promise = registryService.updatePatientAssessmentRecord(this.recordId, assessmentData);
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

        Object.assign(this, patient);

        // Medical information
        this.recordId = patient.recordId ?? this.recordId;
        this.MRN = patient.MRN ?? this.MRN;
        this.name = patient.name;
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
