export interface IUser {
    readonly name: string;
    readonly authToken: string;
}

export interface IPatient {
    readonly firstName: string;
    readonly lastName: string;
    readonly primaryCareManagerName: string;
    readonly clinicCode: string;
}
