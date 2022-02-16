import { IPatient, IValuesInventory } from 'shared/types';

export interface IPatientListResponse {
    message: string;
    patients: IPatient[];
}

export interface IValuesInventoryResponse {
    status: number;
    valuesinventory: IValuesInventory;
}
