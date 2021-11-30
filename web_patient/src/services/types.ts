export type KeyedMap<T> = { [key: string]: T };
export const assessmentFrequencyValues = ['Daily', 'Once a week', 'Every 2 weeks', 'Monthly'] as const;
export type AssessmentFrequency = typeof assessmentFrequencyValues[number];

export interface IUser {
    readonly name: string;
    readonly authToken: string;
}

export type AssessmentData = KeyedMap<number | undefined>;
export interface IAssessmentDataPoint {
    readonly assessmentDataId?: string;
    readonly assessmentId: string;
    readonly date: Date;
    readonly pointValues: AssessmentData;
    comment?: string;
}

export enum DayOfWeekFlags {
    None = 0,
    Sunday = 1 << 0,
    Monday = 1 << 1,
    Tuesday = 1 << 2,
    Wednesday = 1 << 3,
    Thursday = 1 << 4,
    Friday = 1 << 5,
    Saturday = 1 << 6,
    All = ~(~0 << 7),
}

export const daysOfWeekValues = [
    DayOfWeekFlags.Monday,
    DayOfWeekFlags.Tuesday,
    DayOfWeekFlags.Wednesday,
    DayOfWeekFlags.Thursday,
    DayOfWeekFlags.Friday,
    DayOfWeekFlags.Saturday,
    DayOfWeekFlags.Sunday,
] as const;

export interface IActivity {
    id: string;
    name: string;
    value: string;
    lifeareaId: string;
    startDate: Date;
    timeOfDay: number; // hours since midnight
    hasReminder: boolean;
    reminderTimeOfDay: number; // hours since midnight
    hasRepetition: boolean;
    repeatDayFlags: DayOfWeekFlags;
    isActive: boolean;
    isDeleted?: boolean;
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
    readonly interpretationName: string;
    readonly interpretationTable: { score: string; max: number; interpretation: string }[];
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
    lifeareaId: string;
    enjoyment?: number;
    importance?: number;
}

export interface IResourceContent {
    name: string;
    resources: IResourceItem[];
}

export interface IResourceItem {
    name: string;
    filename: string;
}

export const dueTypeValues = ['Exact', 'ChunkOfDay', 'Day', 'Week'];
export type DueType = typeof dueTypeValues[number];

export interface IScheduledTaskItem {
    readonly sourceId: string; // Activity, TODO, or assesment item source
    readonly id: string; // Scheduled item id
    readonly dueType: DueType;
    readonly due: Date;
    readonly name: string;
    readonly reminder: Date;
    completed: boolean;
}

export const assessmentTypeValues = ['PHQ-9', 'GAD-7'];
export type AssessmentType = typeof assessmentTypeValues[number];

export interface IPatientConfig {
    readonly needsInventory: boolean;
    readonly needsSafetyPlan: boolean;
    readonly requiredAssessments: string[];
}

export interface IMoodLog {
    mood: number;
    comment?: string;
}

export const activitySuccessTypeValues = ['Yes', 'SomethingElse', 'No'];
export type ActivitySuccessType = typeof activitySuccessTypeValues[number];

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
