import {
    AssessmentFrequency,
    AssessmentType,
    BehavioralActivationChecklistItem,
    ClinicCode,
    DiscussionFlag,
    FollowupSchedule,
    GAD7Item,
    PatientSex,
    PHQ9Item,
    Referral,
    SessionType,
    TreatmentChange,
    TreatmentPlan,
    TreatmentRegimen,
    TreatmentStatus,
} from 'src/services/enums';

export interface IUser {
    readonly name: string;
    readonly authToken: string;
}

export type BAChecklistMap = { [item in BehavioralActivationChecklistItem]: boolean };
export interface ISession {
    readonly sessionId: number;
    readonly date: Date;
    readonly sessionType: SessionType;
    readonly billableMinutes: number;
    readonly treatmentPlan: TreatmentPlan;
    readonly treatmentChange: TreatmentChange;
    readonly behavioralActivationChecklist: BAChecklistMap;
    readonly sessionNote: string;
}

export interface IAssessment {
    readonly assessmentType: AssessmentType;
    readonly frequency: AssessmentFrequency;
    readonly data: IAssessmentDataPoint[];
}

export type PHQ9Map = { [item in PHQ9Item]: number | undefined };
export type GAD7Map = { [item in GAD7Item]: number | undefined };
export type MoodMap = { ['Mood']: number };

export interface IAssessmentDataPoint {
    readonly date: Date;
    readonly pointValues: PHQ9Map | GAD7Map | MoodMap;
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
