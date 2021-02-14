export type OtherSpecify = 'Other';

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

export type AllClinicCode = 'All Clinics';

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
] as const;
export type TreatmentRegimen = typeof treatmentRegimenValues[number] & OtherSpecify;

export const referralValues = [
    'Psychiatry',
    'Psychology',
    'Pt Navigation',
    'Integrative Medicine',
    'Spiritual Care',
    'Palliative Care',
] as const;
export type Referral = typeof referralValues[number] & OtherSpecify;

export const sessionTypeValues = ['In person at clinic', 'Telehealth', 'Phone', 'Group', 'Home'] as const;
export type SessionType = typeof sessionTypeValues[number] & OtherSpecify;

export const treatmentPlanValues = [
    'Maintain current treatment',
    'Adjust treatment plan',
    'Monitor only',
    'No further follow-up',
    'Refer to community',
] as const;
export type TreatmentPlan = typeof treatmentPlanValues[number];

export const treatmentChangeValues = ['Medication', 'Counseling'] as const;
export type TreatmentChange = typeof treatmentChangeValues[number] & OtherSpecify;

export const behavioralActivationChecklistValues = [
    'Review of the BA model',
    'Values and goals assessment',
    'Activity scheduling',
    'Mood and activity monitoring',
    'Relaxation',
    'Contingency management',
    'Managing avoidance behaviors',
    'Problem-solving',
] as const;

export type BehavioralActivationChecklistItem = typeof behavioralActivationChecklistValues[number];

export const assessmentTypeValues = ['PHQ-9', 'GAD-7', 'Mood logging'] as const;
export type AssessmentType = typeof assessmentTypeValues[number];

export const assessmentFrequencyValues = ['Daily', 'Once a week', 'Every 2 weeks', 'Monthly'] as const;
export type AssessmentFrequency = typeof assessmentFrequencyValues[number];
