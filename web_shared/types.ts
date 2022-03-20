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
    Site,
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

export interface IProviderUser extends IProviderIdentity {
    authToken: string;
    refreshToken: string;
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
    assigned: boolean;
    assignedDateTime?: Date;
    frequency?: AssessmentFrequency;
    dayOfWeek?: DayOfWeek;
}

export interface IActivity {
    activityId?: string;
    name: string;
    value: string;
    lifeareaId: string;
    startDateTime: Date;
    timeOfDay: number;
    hasReminder: boolean;
    reminderTimeOfDay?: number;
    hasRepetition: boolean;
    repeatDayFlags?: DayOfWeekFlags;
    isActive: boolean;
    isDeleted: boolean;
}

export interface IScheduledItem {
    // dueDate: Date; // Contains only the date with 00 time, not used
    dueDateTime: Date; // Contains timezone adjusted date time
    dueType: DueType;
}

export interface IScheduledActivity extends IScheduledItem {
    scheduledActivityId: string;

    activityId: string;
    activityName: string;
    reminder: Date;

    completed: boolean;
}

export interface IScheduledAssessment extends IScheduledItem {
    scheduledAssessmentId: string;

    assessmentId: string;

    completed: boolean;
}
export type AssessmentData = KeyedMap<number | undefined>;

export interface ILog {
    recordedDateTime: Date;
    comment?: string;
}

export interface IActivityLog extends ILog {
    activityLogId?: string;

    scheduledActivityId: string;
    activityId: string;
    activityName: string;

    completed?: boolean;
    success?: ActivitySuccessType;
    alternative?: string;
    pleasure?: number;
    accomplishment?: number;
}

export interface IAssessmentLog extends ILog {
    assessmentLogId?: string;

    scheduledAssessmentId: string;
    assessmentId: string; // NEW

    patientSubmitted?: boolean; // NEW
    submittedByProviderId?: string;
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
    primaryOncologyProvider?: string;
    primaryCareManager?: IProviderIdentity;
    discussionFlag?: DiscussionFlags;
    followupSchedule?: FollowupSchedule;
    depressionTreatmentStatus?: DepressionTreatmentStatus;
    site?: Site;
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
    assignedDateTime?: Date;
    lastUpdatedDateTime?: Date;
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
    assignedScheduledAssessments: IScheduledAssessment[];
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
    patientresources: IResourceContent[];
    registryresources: IResourceContent[];
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
