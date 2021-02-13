import { ClinicCode, DiscussionFlag, FollowupSchedule, PatientSex, TreatmentStatus } from './enums';

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
