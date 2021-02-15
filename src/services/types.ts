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

export interface IUser {
    readonly name: string;
    readonly authToken: string;
}

export interface ISession {
    readonly sessionId: number;
    readonly date: Date;
    readonly sessionType: SessionType;
    readonly billableMinutes: number;
    readonly treatmentPlan: TreatmentPlan;
    readonly treatmentChange: TreatmentChange;
    readonly behavioralActivationChecklist: { [item in BehavioralActivationChecklistItem]: boolean };
    readonly sessionNote: string;
}

export interface IAssessment {
    readonly assessmentType: AssessmentType;
    readonly frequency: AssessmentFrequency;
    readonly data: IAssessmentDataPoint[];
}

export interface IAssessmentDataPoint {
    readonly date: Date;
    readonly pointValue: number;
    readonly comment: string;
}

export interface IActivity {
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
