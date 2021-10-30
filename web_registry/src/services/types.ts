import {
    ActivitySuccessType,
    AssessmentFrequency,
    BehavioralActivationChecklistItem,
    BehavioralStrategyChecklistItem,
    CancerTreatmentRegimen,
    ClinicCode,
    DayOfWeek,
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

export interface ICaseReview {
    reviewId: string;
    date: Date;
    consultingPsychiatrist: string;

    medicationChange: string;
    behavioralStrategyChange: string;
    referralsChange: string;

    otherRecommendations: string;
    reviewNote: string;
}

export type ISessionOrCaseReview = ISession | ICaseReview;

export interface IAssessment {
    readonly assessmentId: string;
    readonly assessmentType: string;
    frequency: AssessmentFrequency;
    dayOfWeek: DayOfWeek;
    readonly data: IAssessmentDataPoint[];
}

export type AssessmentData = KeyedMap<number | undefined>;
export interface IAssessmentDataPoint {
    readonly assessmentDataId: string;
    readonly assessmentType: string; // Redundant, but otherwise, this info needs to be carried some other way.
    readonly date: Date;
    readonly pointValues: AssessmentData;
    readonly comment: string;
    readonly totalScore: number;
    readonly patientSubmitted: boolean;
}

export interface IActivity {
    readonly activityId: string;
    readonly activityName: string;
    readonly moodData: IAssessmentDataPoint[];
}

export interface IActivityLog {
    id: string;
    date: Date;
    activityId: string;
    activityName: string;
    success: ActivitySuccessType;
    alternative: string;
    pleasure: number;
    accomplishment: number;
    comment: string;
}

export interface IPatientProfile {
    recordId: string;
    name: string;
    MRN: string;
    clinicCode: ClinicCode;
    birthdate: Date;
    sex: PatientSex;
    gender: PatientGender;
    pronoun: PatientPronoun;
    race: PatientRaceEthnicity;
    primaryOncologyProvider: string;
    primaryCareManager: string;
    discussionFlag: DiscussionFlags;
    followupSchedule: FollowupSchedule;
    depressionTreatmentStatus: DepressionTreatmentStatus;
}

export interface IClinicalHistory {
    primaryCancerDiagnosis: string;
    dateOfCancerDiagnosis: string;
    currentTreatmentRegimen: CancerTreatmentRegimenFlags;
    currentTreatmentRegimenOther: string;
    currentTreatmentRegimenNotes: string;
    psychDiagnosis: string;
    pastPsychHistory: string;
    pastSubstanceUse: string;
    psychSocialBackground: string;
}

export interface IValuesInventory {
    assigned: boolean;
    assignedDate: Date;
    values: ILifeAreaValue[];
}

export interface ISafetyPlan {
    assigned: boolean;
    assignedDate: Date;
}

export type CancerTreatmentRegimenFlags = { [item in CancerTreatmentRegimen]: boolean };
export type DiscussionFlags = { [item in DiscussionFlag]: boolean };

export interface IPatient extends IPatientProfile, IClinicalHistory {
    // Sessions
    readonly sessions: ISession[];
    readonly caseReviews: ICaseReview[];

    // Assessments
    readonly assessments: IAssessment[];

    // Values inventory
    readonly valuesInventory: IValuesInventory;

    // Activities
    readonly activities: IActivity[];

    // Activity logs
    readonly activityLogs: IActivityLog[];
}

export interface IPatientList {
    readonly patients: IPatient[];
}

export interface IAppConfig {
    assessments: IAssessmentContent[];
    lifeAreas: ILifeAreaContent[];
    resources: IResourceContent[];
}

export interface IAssessmentContent {
    readonly id: string;
    readonly name: string;
    readonly instruction: string;
    readonly questions: { question: string; id: string }[];
    readonly options: { text: string; value: number }[];
}

export interface ILifeAreaContent {
    readonly id: string;
    readonly name: string;
    readonly examples: ILifeAreaValue[];
}

export interface ILifeAreaValue {
    id: string;
    name: string;
    lifeareaId: string;
    activities: ILifeAreaValueActivity[];
}

export interface ILifeAreaValueActivity {
    id: string;
    name: string;
    valueId: string;
    dateCreated: Date;
    dateEdited: Date;
    lifeareaId: string;
    enjoyment?: number;
    importance?: number;
}

export interface IResourceContent {
    id: string;
    name: string;
    resources: IResourceItem[];
}

export interface IResourceItem {
    name: string;
    filename: string;
}

export const isSession = (session: ISession | ICaseReview): session is ISession => {
    return (session as ISession)?.sessionId !== undefined;
};
