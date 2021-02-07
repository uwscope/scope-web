export const patientSexValues = ['Male', 'Female'] as const;
export type PatientSex = typeof patientSexValues[number];

export const clinicCodeValues = [
    'Breast',
    'Endocrine',
    'GI',
    'GI – Pancreatic',
    'GU',
    'GYN',
    'HEME',
    'HEME – Sickle Cell',
    'HNL',
    'Immunotherapy',
    'Melanoma/Renal',
    'Neuro',
    'NW Hospital',
    'Sarcoma',
    'Transplant – Auto',
    'Transplant – Allo',
    'Transplant – CAR-T',
    'Transplant – LTFU',
    'Transplant – TTC',
] as const;
export type ClinicCode = typeof clinicCodeValues[number];

export const treatmentStatusValues = [
    'Active',
    'Active Distressed',
    'Deceased',
    'Discharged',
    'Followed by Outside MHP ONLY',
    'Followed by Psych ONLY',
    'Relapse Prevention (already included)',
    'Inactive (already included)',
    'Continued',
] as const;
export type TreatmentStatus = typeof treatmentStatusValues[number];

export const followupScheduleValues = ['1-week follow-up', '2-week follow-up', '4-week follow-up'] as const;
export type FollowupSchedule = typeof followupScheduleValues[number];

export const discussionFlagValues = [
    'Flag as safety risk',
    'Flag for discussion',
    'Flag for discussion & safety risk',
] as const;
export type DiscussionFlag = typeof discussionFlagValues[number];

export interface IUser {
    readonly name: string;
    readonly authToken: string;
}

export interface IPatient {
    // Basic information
    readonly MRN: number;
    readonly firstName: string;
    readonly lastName: string;
    readonly birthdate: Date;
    readonly sex: PatientSex;

    // Treatment information
    readonly primaryCareManagerName: string;
    readonly treatmentStatus: TreatmentStatus;
    readonly clinicCode: ClinicCode;
    readonly followupSchedule: FollowupSchedule;
    readonly discussionFlag: DiscussionFlag;

    // Notes
    readonly notes: string;
}

// export const TEST_getRandomPatientSex = () => {
//     return patientSexValues[Math.floor(Math.random() * patientSexValues.length)];
// };

// export const TEST_getRandomClinicCode = () => {
//     return clinicCodeValues[Math.floor(Math.random() * clinicCodeValues.length)];
// };

// export const TEST_getRandomTreatmentStatus = () => {
//     return treatmentStatusValues[Math.floor(Math.random() * treatmentStatusValues.length)];
// };

// export const TEST_getRandomFollowupSchedule = () => {
//     return followupScheduleValues[Math.floor(Math.random() * followupScheduleValues.length)];
// };

// export const TEST_getRandomDiscussionFlag = () => {
//     return discussionFlagValues[Math.floor(Math.random() * discussionFlagValues.length)];
// };
