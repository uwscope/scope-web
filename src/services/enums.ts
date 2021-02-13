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

export const treatmentRegimenValues = [
    'Surgery',
    'Chemotherapy',
    'Radiation',
    'Stem Cell Transplant',
    'Immunotherapy',
    'CAR-T',
    'Endocrine',
    'Surveillance',
    'Other',
] as const;
export type TreatmentRegimen = typeof treatmentRegimenValues[number];

export const referralValues = [
    'Psychiatry',
    'Psychology',
    'Pt Navigation',
    'Integrative Medicine',
    'Spiritual Care',
    'Palliative Care',
    'Other',
] as const;
export type Referral = typeof referralValues[number];
