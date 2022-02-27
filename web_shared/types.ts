import {
    ActivitySuccessType,
    AssessmentFrequency,
    BAChecklistFlags,
    BehavioralStrategyChecklistFlags,
    CancerTreatmentRegimenFlags,
    ClinicCode,
    DayOfWeek,
    DayOfWeekFlags,
    DepressionTreatmentStatus,
    DiscussionFlags,
    DueType,
    FollowupSchedule,
    OtherSpecify,
    PatientEthnicity,
    PatientGender,
    PatientPronoun,
    PatientRaceFlags,
    PatientSex,
    ProviderRole,
    Referral,
    ReferralStatus,
    SessionType,
} from './enums';

export type KeyedMap<T> = { [key: string]: T };

export interface IIdentity {
    name: string;
}

export interface IPatientIdentity extends IIdentity {
    patientId: string;
}

export interface IProviderIdentity extends IIdentity {
    providerId: string;
    role: ProviderRole;
}

export interface IPatientUser extends IPatientIdentity {
    authToken: string;
}

export interface IProviderUser extends IProviderIdentity {
    authToken: string;
}

export interface IReferralStatus {
    referralType: Referral | OtherSpecify;
    referralStatus: ReferralStatus;
    referralOther?: string; // If the referralType is Other, then provide the detail in this field
}

export type ISessionOrCaseReview = ISession | ICaseReview;

export interface ISession {
    sessionId?: string;
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
    referrals: IReferralStatus[];

    otherRecommendations: string;
    sessionNote: string;
}

export interface ICaseReview {
    caseReviewId?: string;
    date: Date;
    consultingPsychiatrist: IProviderIdentity;

    medicationChange: string;
    behavioralStrategyChange: string;
    referralsChange: string;

    otherRecommendations: string;
    reviewNote: string;
}

export interface IAssessment {
    assessmentId: string;
    assessmentName: string;
    assigned: boolean;
    assignedDate: Date;
    frequency: AssessmentFrequency;
    dayOfWeek: DayOfWeek;
}

export interface IActivity {
    activityId?: string;
    name: string;
    value: string;
    lifeareaId: string;
    startDate: Date;
    timeOfDay: number;
    hasReminder: boolean;
    reminderTimeOfDay: number;
    hasRepetition: boolean;
    repeatDayFlags: DayOfWeekFlags;
    isActive: boolean;
    isDeleted: boolean;
}

export interface IScheduledItem {
    scheduleId: string;
    dueDate: Date;
    dueType: DueType;
}

export interface IScheduledActivity extends IScheduledItem {
    activityId: string;
    activityName: string;
    reminder: Date;

    completed: boolean;
}

export interface IScheduledAssessment extends IScheduledItem {
    assessmentId: string;
    assessmentName: string;

    completed: boolean;
}
export type AssessmentData = KeyedMap<number | undefined>;

export interface ILog {
    logId?: string; // Should these be optional until committed?
    recordedDate: Date;
    comment?: string;
}

export interface IActivityLog extends ILog {
    scheduleId: string;
    activityName: string;

    completed?: boolean;
    success?: ActivitySuccessType;
    alternative?: string;
    pleasure?: number;
    accomplishment?: number;
}

export interface IAssessmentLog extends ILog {
    scheduleId: string;
    assessmentId: string; // NEW
    assessmentName: string;

    completed: boolean;
    patientSubmitted?: boolean; // NEW
    submittedBy?: IIdentity;
    pointValues: AssessmentData;
    totalScore?: number;
}

export interface IMoodLog extends ILog {
    moodLogId?: string;
    mood: number;
}

export interface IPatientProfile {
    name: string;
    MRN: string;
    clinicCode?: ClinicCode;
    birthdate?: Date;
    sex?: PatientSex;
    gender?: PatientGender;
    pronoun?: PatientPronoun;
    race?: PatientRaceFlags;
    ethnicity?: PatientEthnicity;
    primaryOncologyProvider?: IIdentity;
    primaryCareManager?: IIdentity;
    discussionFlag?: DiscussionFlags;
    followupSchedule?: FollowupSchedule;
    depressionTreatmentStatus?: DepressionTreatmentStatus;
}

export interface IClinicalHistory {
    primaryCancerDiagnosis?: string;
    // Date is a string to allow flexibility for social worker.
    // This particular date is never used for any computations.
    dateOfCancerDiagnosis?: string;
    currentTreatmentRegimen?: CancerTreatmentRegimenFlags;
    currentTreatmentRegimenOther?: string;
    currentTreatmentRegimenNotes?: string;
    psychDiagnosis?: string;
    pastPsychHistory?: string;
    pastSubstanceUse?: string;
    psychSocialBackground?: string;
}

export interface IContact {
    name: string;
    address?: string;
    phoneNumber?: string;
    emergencyNumber?: string;
}

export interface ISafetyPlan {
    assigned: boolean;
    assignedDate?: Date;
    lastUpdatedDate?: Date;
    reasonsForLiving?: string;
    warningSigns?: string[];
    copingStrategies?: string[];
    socialDistractions?: IContact[];
    settingDistractions?: string[];
    supporters?: IContact[];
    professionals?: IContact[];
    urgentServices?: IContact[];
    safeEnvironment?: string[];
}

export interface IValuesInventory {
    assigned: boolean;
    assignedDateTime?: Date;
    lastUpdatedDateTime?: Date;
    values?: ILifeAreaValue[];
}

export interface ILifeAreaContent {
    id: string;
    name: string;
    examples: ILifeAreaValue[];
}

export interface ILifeAreaValue {
    name: string;
    createdDateTime: Date;
    editedDateTime: Date;
    lifeareaId: string;
    activities: ILifeAreaValueActivity[];
}

export interface ILifeAreaValueActivity {
    name: string;
    createdDateTime: Date;
    editedDateTime: Date;
    enjoyment?: number;
    importance?: number;
}

export interface IPatient {
    identity: IPatientIdentity;

    // Patient info
    profile: IPatientProfile;
    clinicalHistory: IClinicalHistory;

    // Values inventory and safety plan
    valuesInventory: IValuesInventory;
    safetyPlan: ISafetyPlan;

    // Sessions
    sessions: ISession[];
    caseReviews: ICaseReview[];

    // Assessments
    assessments: IAssessment[];
    scheduledAssessments: IScheduledAssessment[];
    assessmentLogs: IAssessmentLog[];

    // Activities
    activities: IActivity[];
    scheduledActivities: IScheduledActivity[];
    activityLogs: IActivityLog[];

    // Mood logs
    moodLogs: IMoodLog[];
}

export interface IPatientList {
    patients: IPatient[];
}

export interface IPatientConfig {
    assignedValuesInventory: boolean;
    assignedSafetyPlan: boolean;
    assignedAssessmentIds: string[];
}

export interface IAppConfig {
    auth: IAppAuthConfig;
    content: IAppContentConfig;
}

export interface IAppAuthConfig {
    poolid: string;
    clientid: string;
}

export interface IAppContentConfig {
    assessments: IAssessmentContent[];
    lifeAreas: ILifeAreaContent[];
    resources: IResourceContent[];
}

export interface IAssessmentContent {
    id: string;
    name: string;
    instruction: string;
    questions: { question: string; id: string }[];
    options: { text: string; value: number }[];
    interpretationName: string;
    interpretationTable: { score: string; max: number; interpretation: string }[];
}

export interface ILifeAreaContent {
    id: string;
    name: string;
    examples: ILifeAreaValue[];
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
