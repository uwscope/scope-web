export type OtherSpecify = 'Other';

export const patientSexValues = ['Male', 'Female'] as const;
export type PatientSex = typeof patientSexValues[number];

export const patientGenderValues = ['Male', 'Female'] as const;
export type PatientGender = typeof patientGenderValues[number];

export const patientPronounValues = ['He/Him', 'She/Her', 'They/Them'] as const;
export type PatientPronoun = typeof patientPronounValues[number];

export const patientRaceEthnicityValues = ['White', 'Black'] as const;
export type PatientRaceEthnicity = typeof patientRaceEthnicityValues[number];

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
    'Other',
] as const;
export type ClinicCode = typeof clinicCodeValues[number];

export type AllClinicCode = 'All Clinics';

export const depressionTreatmentStatusValues = ['CoCM', 'CoCM Relapse Prevention', 'Discharged', 'Pending'] as const;
export type DepressionTreatmentStatus = typeof depressionTreatmentStatusValues[number] | OtherSpecify;

export const followupScheduleValues = ['1-week follow-up', '2-week follow-up', '4-week follow-up'] as const;
export type FollowupSchedule = typeof followupScheduleValues[number];

export const discussionFlagValues = ['Flag as safety risk', 'Flag for discussion'] as const;
export type DiscussionFlag = typeof discussionFlagValues[number];

export const cancerTreatmentRegimenValues = [
    'Surgery',
    'Chemotherapy',
    'Radiation',
    'Stem Cell Transplant',
    'Immunotherapy',
    'CAR-T',
    'Endocrine',
    'Surveillance',
] as const;
export type CancerTreatmentRegimen = typeof cancerTreatmentRegimenValues[number] | OtherSpecify;

export const referralValues = [
    'Psychiatry',
    'Psychology',
    'Patient Navigation',
    'Integrative Medicine',
    'Spiritual Care',
    'Palliative Care',
] as const;
export type Referral = typeof referralValues[number] | OtherSpecify;

export const referralStatusValues = ['Not Referred', 'Pending', 'Active', 'Completed'] as const;
export type ReferralStatus = typeof referralStatusValues[number];

export const sessionTypeValues = ['In person', 'Telehealth', 'Phone', 'Group', 'Home'] as const;
export type SessionType = typeof sessionTypeValues[number] | OtherSpecify;

export const treatmentPlanValues = [
    'Maintain current treatment',
    'Adjust treatment plan',
    'Monitor only',
    'No further follow-up',
    'Refer to community',
] as const;
export type TreatmentPlan = typeof treatmentPlanValues[number];

export const treatmentChangeValues = ['None', 'Medication', 'Counseling'] as const;
export type TreatmentChange = typeof treatmentChangeValues[number] | OtherSpecify;

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

export const behavioralStrategyChecklistValues = [
    'Behavioral Activation',
    'Motivational Interviewing',
    'Problem Solving Therapy',
    'Cognitive Therapy',
    'Mindfulness Strategies',
    'Supportive Therapy',
] as const;
export type BehavioralStrategyChecklistItem = typeof behavioralStrategyChecklistValues[number] | OtherSpecify;

export const assessmentFrequencyValues = ['Daily', 'Once a week', 'Every 2 weeks', 'Monthly', 'None'] as const;
export type AssessmentFrequency = typeof assessmentFrequencyValues[number];

export const phq9ItemValues = [
    'Interest',
    'Feeling',
    'Sleep',
    'Tired',
    'Apetite',
    'Failure',
    'Concentrating',
    'Slowness',
    'Suicide',
] as const;
export type PHQ9Item = typeof phq9ItemValues[number];

export const gad7ItemValues = [
    'Anxious',
    'Constant worrying',
    'Worrying too much',
    'Trouble relaxing',
    'Restless',
    'Irritable',
    'Afraid',
] as const;
export type GAD7Item = typeof gad7ItemValues[number];

export type CaseReviewEntryType = 'Case Review';
export type SessionEntryType = 'Session';
export type EntryType = SessionEntryType | CaseReviewEntryType;

export const daysOfWeekValues = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'] as const;

export type DayOfWeek = typeof daysOfWeekValues[number];

export const activitySuccessTypeValues = ['Yes', 'SomethingElse', 'No'];
export type ActivitySuccessType = typeof activitySuccessTypeValues[number];
