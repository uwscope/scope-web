import { IPatient, IPatientProfile, IValuesInventory } from 'shared/types';

interface IServiceResponse {
    status: number;
    message?: string;
}

export interface IPatientListResponse extends IServiceResponse {
    patients: IPatient[];
}

export interface IPatientResponse extends IServiceResponse {
    patient: IPatient;
}

export interface IPatientProfileRequest {
    profile: IPatientProfile;
}

export interface IPatientProfileResponse extends IServiceResponse {
    profile: IPatientProfile;
}

export interface IValuesInventoryRequest {
    valuesinventory: IValuesInventory;
}

export interface IValuesInventoryResponse extends IServiceResponse {
    valuesinventory: IValuesInventory;
}

export interface IQuoteResponse extends IServiceResponse {
    quote: string;
}
