import { IPatient, IValuesInventory } from 'shared/types';

interface IServiceResponse {
    status: number;
}

export interface IPatientListResponse extends IServiceResponse {
    message: string;
    patients: IPatient[];
}

export interface IPatientResponse extends IServiceResponse {
    patient: IPatient;
}

export interface IValuesInventoryResponse extends IServiceResponse {
    valuesinventory: IValuesInventory;
}

export interface IQuoteResponse extends IServiceResponse {
    quote: { quote: string };
}
