import {
    ActivitySuccessType,
    AssessmentFrequency,
    BAChecklistFlags,
    BehavioralStrategyChecklistFlags,
    CancerTreatmentRegimenFlags,
    ClinicCode,
    ContactType,
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
    Referral,
    ReferralStatus,
    SessionType,
} from './enums';

export type KeyedMap<T> = { [key: string]: T };

export interface IUser extends IIdentity {
    authToken: string;
}

export interface IIdentity {
    identityId: string;
    name: string;
}

export interface IReferralStatus {
    referralType: Referral | OtherSpecify;
    referralStatus: ReferralStatus;
    referralOther?: string; // If the referralType is Other, then provide the detail in this field
}

export type ISessionOrCaseReview = ISession | ICaseReview;

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
    referrals: IReferralStatus[];

    otherRecommendations: string;
    sessionNote: string;
}

export interface ICaseReview {
    reviewId: string;
    date: Date;
    consultingPsychiatrist: IIdentity;

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
    activityId: string;
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
    contactType: ContactType;
    name: string;
    address?: string;
    phoneNumber?: string;
    emergencyNumber?: string;
}

export interface ISafetyPlan {
    assigned: boolean;
    assignedDate: Date;
    lastUpdatedDate?: Date;
    reasonsForLiving?: string;
    warningSigns?: string[];
    copingStrategies?: string[];
    distractions?: (string | IContact)[];
    supporters?: IContact[];
    professionalSupporters?: IContact[];
    urgentServices?: IContact[];
    safeEnvironment?: string[];
}

export interface IValuesInventory {
    assigned: boolean;
    assignedDate: Date;
    lastUpdatedDate?: Date;
    values?: ILifeAreaValue[];
}

export interface ILifeAreaContent {
    id: string;
    name: string;
    examples: ILifeAreaValue[];
}

export interface ILifeAreaValue {
    id: string;
    name: string;
    dateCreated: Date;
    dateEdited: Date;
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

export interface IPatient {
    identity: IIdentity;

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

export interface IAppConfig {
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

export interface IPatientConfig {
    assignedValuesInventory: boolean;
    assignedSafetyPlan: boolean;
    assignedAssessmentIds: string[];
}

export interface IAppConfig {
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
