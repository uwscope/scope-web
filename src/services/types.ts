import {
    AssessmentFrequency,
    AssessmentType,
    BehavioralActivationChecklistItem,
    ClinicCode,
    DiscussionFlag,
    FollowupSchedule,
    PatientSex,
    Referral,
    SessionType,
    TreatmentChange,
    TreatmentPlan,
    TreatmentRegimen,
    TreatmentStatus,
} from 'src/services/enums';

export interface IUser {
    readonly name: string;
    readonly authToken: string;
}

export interface ISession {
    readonly sessionId: number;
    readonly date: Date;
    readonly sessionType: SessionType;
    readonly billableMinutes: number;
    readonly treatmentPlan: TreatmentPlan;
    readonly treatmentChange: TreatmentChange;
    readonly behavioralActivationChecklist: { [item in BehavioralActivationChecklistItem]: boolean };
    readonly sessionNote: string;
}

export interface IAssessment {
    readonly assessmentType: AssessmentType;
    readonly frequency: AssessmentFrequency;
    readonly data: IAssessmentDataPoint[];
}

export interface IAssessmentDataPoint {
    readonly date: Date;
    readonly pointValue: number;
    readonly comment: string;
}

export interface IActivity {
    readonly activityName: string;
    readonly moodData: IAssessmentDataPoint[];
}

export interface IPatient {
    // Medical information
    readonly MRN: number;
    readonly firstName: string;
    readonly lastName: string;
    readonly birthdate: Date;
    readonly sex: PatientSex;
    readonly clinicCode: ClinicCode;
    readonly treatmentRegimen: TreatmentRegimen;
    readonly medicalDiagnosis: string;

    // Treatment information
    readonly primaryCareManagerName: string;
    readonly treatmentStatus: TreatmentStatus;
    readonly followupSchedule: FollowupSchedule;
    readonly discussionFlag: DiscussionFlag;
    readonly referral: Referral;
    readonly treatmentPlan: string;

    // Psychiatry
    readonly psychHistory: string;
    readonly substanceUse: string;
    readonly psychMedications: string;
    readonly psychDiagnosis: string;

    // Sessions
    readonly sessions: ISession[];

    // Assessments
    readonly assessments: IAssessment[];

    // Activities
    readonly activities: IActivity[];
}
