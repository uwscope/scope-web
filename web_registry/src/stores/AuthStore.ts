import { AuthenticationDetails, CognitoUser, CognitoUserPool, CognitoUserSession } from 'amazon-cognito-identity-js';
import { action, makeAutoObservable } from 'mobx';
import { IUser } from 'shared/types';
import { PromiseQuery } from 'src/services/promiseQuery';
import { IPatientsStore, PatientsStore } from 'src/stores/PatientsStore';

const poolData = {
    UserPoolId: 'us-west-1_G5EgsKP1m',
    ClientId: 'mcn1gm8i1ih1r8cfdtaobailo',
};

const UserPool = new CognitoUserPool(poolData);

export enum AuthState {
    Initialized,
    NewPasswordRequired,
    Authenticated,
    AuthenticationFailed,
}

export interface IAuthStore {
    authState: AuthState;
    authUser?: CognitoUser;
    authData?: any; // User attribute data

    currentUserIdentity?: IUser;
    login(username: string, password: string): Promise<CognitoUserSession>;
    updateTempPassword(newPassword: string): Promise<CognitoUserSession>;
    logout(): void;
}

export class AuthStore implements IAuthStore {
    public authState = AuthState.Initialized;

    public authUser?: CognitoUser;
    public authData?: any;

    public currentUserIdentity?: IUser;
    public patientsStore: IPatientsStore;

    // App metadata
    public appTitle = 'SCOPE Registry';

    // Promise queries
    private readonly authQuery: PromiseQuery<CognitoUserSession>;

    constructor() {
        this.patientsStore = new PatientsStore();

        this.authQuery = new PromiseQuery<CognitoUserSession>(undefined, 'authQuery');

        makeAutoObservable(this);
    }

    @action.bound
    public async login(username: string, password: string) {
        const authUser = new CognitoUser({
            Username: username,
            Pool: UserPool,
        });

        const authDetails = new AuthenticationDetails({
            Username: username,
            Password: password,
        });

        const promise = new Promise<CognitoUserSession>((resolve, reject) => {
            authUser.authenticateUser(authDetails, {
                onSuccess: action((data) => {
                    console.log('onLoginSuccess: ', data);
                    this.authUser = authUser;
                    this.authData = undefined;
                    this.authState = AuthState.Authenticated;
                    resolve(data);
                }),
                onFailure: action((err) => {
                    console.error('onLoginFailure: ', err);
                    this.authUser = undefined;
                    this.authData = undefined;
                    this.authState = AuthState.AuthenticationFailed;
                    reject(err);
                }),
                newPasswordRequired: action((data: CognitoUser) => {
                    console.log('newPasswordRequired: ', data);
                    this.authUser = authUser;
                    this.authData = data;
                    this.authState = AuthState.NewPasswordRequired;
                    reject('newPasswordRequired');
                }),
            });
        });

        return await this.authQuery.fromPromise(promise);
    }

    @action.bound
    public async updateTempPassword(password: string) {
        const promise = new Promise<CognitoUserSession>((resolve, reject) => {
            this.authUser?.completeNewPasswordChallenge(password, this.authData, {
                onSuccess: action((data) => {
                    console.log('onUpdateSuccess: ', data);
                    this.authData = undefined;
                    this.authState = AuthState.Authenticated;

                    console.log('authdata', this.authData);
                    resolve(data);
                }),
                onFailure: action((err) => {
                    console.error('onUpdateFailure: ', err);
                    this.authUser = undefined;
                    this.authData = undefined;
                    this.authState = AuthState.AuthenticationFailed;
                    reject(err);
                }),
            });
        });

        return await this.authQuery.fromPromise(promise);
    }

    @action.bound
    public logout() {
        this.authUser?.signOut();
        this.authState = AuthState.Initialized;
        this.authUser = undefined;
        this.authData = undefined;
    }
}
