import {
    AssessmentFrequency,
    BehavioralActivationChecklistItem,
    CancerTreatmentRegimen,
    ClinicCode,
    DepressionTreatmentStatus,
    DiscussionFlag,
    FollowupSchedule,
    PatientSex,
    SessionType,
    TreatmentChange,
    TreatmentPlan,
} from 'src/services/enums';

export type KeyedMap<T> = { [key: string]: T };

export interface IUser {
    readonly name: string;
    readonly authToken: string;
}

export type BAChecklistMap = { [item in BehavioralActivationChecklistItem]: boolean };
export interface ISession {
    readonly sessionId: string;
    readonly date: Date;
    readonly sessionType: SessionType;
    readonly billableMinutes: number;
    readonly treatmentPlan: TreatmentPlan;
    readonly treatmentChange: TreatmentChange;
    readonly behavioralActivationChecklist: BAChecklistMap;
    readonly sessionNote: string;
}

export interface IAssessment {
    readonly assessmentId: string;
    readonly assessmentType: string;
    readonly frequency: AssessmentFrequency;
    readonly data: IAssessmentDataPoint[];
}

export type AssessmentData = KeyedMap<number | undefined>;
export interface IAssessmentDataPoint {
    readonly assessmentDataId: string;
    readonly assessmentType: string; // Redundant, but otherwise, this info needs to be carried some other way.
    readonly date: Date;
    readonly pointValues: AssessmentData;
    readonly comment: string;
}

export interface IActivity {
    readonly activityId: string;
    readonly activityName: string;
    readonly moodData: IAssessmentDataPoint[];
}

export interface IMedicalInfo {
    primaryCareManager: string;
    sex: PatientSex;
    birthdate: Date;
    clinicCode: ClinicCode;
}

export interface IClinicalHistory {
    primaryCancerDiagnosis: string;
    pastPsychHistory: string;
    pastSubstanceUse: string;
}

export type CancerTreatmentRegimenFlags = { [item in CancerTreatmentRegimen]: boolean };
export type DiscussionFlags = { [item in DiscussionFlag]: boolean };
export interface ITreatmentInfo {
    currentTreatmentRegimen: CancerTreatmentRegimenFlags;
    currentTreatmentRegimenOther: string;
    depressionTreatmentStatus: DepressionTreatmentStatus;
    psychDiagnosis: string;
    discussionFlag: DiscussionFlags;
    followupSchedule: FollowupSchedule;
}

export interface IPatient extends IMedicalInfo, IClinicalHistory, ITreatmentInfo {
    readonly MRN: number;
    readonly firstName: string;
    readonly lastName: string;

    // Sessions
    readonly sessions: ISession[];

    // Assessments
    readonly assessments: IAssessment[];

    // Activities
    readonly activities: IActivity[];
}

export interface IPatientList {
    readonly patients: IPatient[];
}

export interface IAppConfig {
    assessments: IAssessmentContent[];
}

export interface IAssessmentContent {
    readonly name: string;
    readonly instruction: string;
    readonly questions: { question: string; id: string }[];
    readonly options: { text: string; value: number }[];
}
