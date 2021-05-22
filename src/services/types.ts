import {
    AssessmentFrequency,
    BehavioralActivationChecklistItem,
    BehavioralStrategyChecklistItem,
    CancerTreatmentRegimen,
    ClinicCode,
    DepressionTreatmentStatus,
    DiscussionFlag,
    FollowupSchedule,
    PatientGender,
    PatientPronoun,
    PatientRaceEthnicity,
    PatientSex,
    Referral,
    ReferralStatus,
    SessionType,
} from 'src/services/enums';

export type KeyedMap<T> = { [key: string]: T };

export interface IUser {
    readonly name: string;
    readonly authToken: string;
}

export type BAChecklistFlags = { [item in BehavioralActivationChecklistItem]: boolean };
export type BehavioralStrategyChecklistFlags = { [item in BehavioralStrategyChecklistItem]: boolean };
export type ReferralStatusFlags = { [item in Referral]: ReferralStatus };

export interface ISession {
    sessionId: string;
    date: Date;
    sessionType: SessionType;
    billableMinutes: number;

    // Medications
    medicationChange: string;
    currentMedications: string;

    // Behavioral strategies
    behavioralStrategyChecklist: BehavioralStrategyChecklistFlags;
    behavioralStrategyOther: string;
    behavioralActivationChecklist: BAChecklistFlags;

    // Referrals
    referralStatus: ReferralStatusFlags;
    referralOther: string;

    otherRecommendations: string;
    sessionNote: string;
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

export interface IPatientProfile {
    recordId: string;
    name: string;
    MRN: string;
    clinicCode: ClinicCode;
    depressionTreatmentStatus: DepressionTreatmentStatus;
    birthdate: Date;
    sex: PatientSex;
    gender: PatientGender;
    pronoun: PatientPronoun;
    race: PatientRaceEthnicity;
    primaryOncologyProvider: string;
    primaryCareManager: string;
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
    currentTreatmentRegimenNotes: string;
    psychDiagnosis: string;
    discussionFlag: DiscussionFlags;
    followupSchedule: FollowupSchedule;
}

export interface IPatient extends IPatientProfile, IClinicalHistory, ITreatmentInfo {
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
