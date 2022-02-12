import { IPatient } from 'shared/types';

export interface IPatientListResponse {
    message: string;
    patients: IPatient[];
}
