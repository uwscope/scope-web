import {
    AssessmentFrequency,
    AssessmentType,
    BehavioralActivationChecklistItem,
    ClinicCode,
    DiscussionFlag,
    FollowupSchedule,
    PatientSex,
    Referral,
    SessionType,
    TreatmentChange,
    TreatmentPlan,
    TreatmentRegimen,
    TreatmentStatus,
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
    readonly assessmentType: AssessmentType;
    readonly frequency: AssessmentFrequency;
    readonly data: IAssessmentDataPoint[];
}

export type AssessmentData = KeyedMap<number | undefined>;
export interface IAssessmentDataPoint {
    readonly assessmentDataId: string;
    readonly assessmentType: AssessmentType; // Redundant, but otherwise, this info needs to be carried some other way.
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
    treatmentRegimen: TreatmentRegimen;
    medicalDiagnosis: string;
}

export interface ITreatmentInfo {
    treatmentStatus: TreatmentStatus;
    followupSchedule: FollowupSchedule;
    discussionFlag: DiscussionFlag;
    referral: Referral;
    treatmentPlan: string;
}

export interface IPsychiatryInfo {
    psychHistory: string;
    substanceUse: string;
    psychMedications: string;
    psychDiagnosis: string;
}

export interface IPatient extends IMedicalInfo, ITreatmentInfo, IPsychiatryInfo {
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
