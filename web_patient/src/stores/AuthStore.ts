import { AuthenticationDetails, CognitoUser, CognitoUserPool, CognitoUserSession } from 'amazon-cognito-identity-js';
import { action, computed, makeAutoObservable, runInAction } from 'mobx';
import {IAppAuthConfig, IPatientUser} from 'shared/types';
import { PromiseQuery } from 'shared/promiseQuery';

export enum AuthState {
    Initialized,
    NewPasswordRequired,
    Authenticated,
    AuthenticationFailed,
}

export interface IAuthStore {
    isAuthenticated: boolean;
    authState: AuthState;
    authUser?: CognitoUser;

    currentUserIdentity?: IPatientUser;
    login(username: string, password: string): Promise<CognitoUserSession>;
    updateTempPassword(newPassword: string): Promise<CognitoUserSession>;
    logout(): void;
}

export class AuthStore implements IAuthStore {
    public authConfig: IAppAuthConfig;

    public authState = AuthState.Initialized;

    public authUser?: CognitoUser;

    // Promise queries
    private readonly authQuery: PromiseQuery<CognitoUserSession>;

    constructor(authConfig: IAppAuthConfig) {
        this.authConfig = authConfig;

        this.authQuery = new PromiseQuery<CognitoUserSession>(undefined, 'authQuery');

        makeAutoObservable(this);
    }

    @computed
    public get isAuthenticated() {
        return this.authState == AuthState.Authenticated;
    }

    @computed
    public get currentUserIdentity() {
        if (this.authState == AuthState.Authenticated) {
            var idToken = this.authQuery.value?.getIdToken();

            if (idToken?.payload['sub'] && idToken?.getJwtToken()) {
                return {
                    patientId: "persistent", // idToken?.payload['sub'],
                    name: "TODO", // idToken?.payload['name'],
                    authToken: idToken?.getJwtToken(),
                } as IPatientUser;
            }
        }

        return undefined;
    }

    @action.bound
    public async login(username: string, password: string) {
        const authUser = new CognitoUser({
            Username: username,
            Pool: new CognitoUserPool({
                UserPoolId: this.authConfig.poolid,
                ClientId: this.authConfig.clientid,
            }),
        });

        const authDetails = new AuthenticationDetails({
            Username: username,
            Password: password,
        });

        const promise = new Promise<CognitoUserSession>((resolve, reject) => {
            authUser.authenticateUser(authDetails, {
                onSuccess: action((data) => {
                    console.log('onLoginSuccess: ', data);
                    runInAction(() => {
                        this.authUser = authUser;
                        this.authState = AuthState.Authenticated;
                    });
                    resolve(data);
                }),
                onFailure: action((err) => {
                    console.error('onLoginFailure: ', err);
                    runInAction(() => {
                        this.authUser = undefined;

                        this.authState = AuthState.AuthenticationFailed;
                    });
                    reject(err);
                }),
                newPasswordRequired: action((data: CognitoUser) => {
                    console.log('newPasswordRequired: ', data);
                    runInAction(() => {
                        this.authUser = authUser;
                        this.authState = AuthState.NewPasswordRequired;
                    });
                    reject('newPasswordRequired');
                }),
            });
        });

        return await this.authQuery.fromPromise(promise);
    }

    @action.bound
    public async updateTempPassword(password: string) {
        const promise = new Promise<CognitoUserSession>((resolve, reject) => {
            this.authUser?.completeNewPasswordChallenge(
                password,
                {}, // No additional required fields to set/update
                {
                    onSuccess: action((data) => {
                        console.log('onUpdateSuccess: ', data);
                        runInAction(() => {
                            this.authState = AuthState.Authenticated;
                        });
                        resolve(data);
                    }),
                    onFailure: action((err) => {
                        console.error('onUpdateFailure: ', err);
                        runInAction(() => {
                            this.authUser = undefined;
                            this.authState = AuthState.AuthenticationFailed;
                        });
                        reject(err);
                    }),
                }
            );
        });

        return await this.authQuery.fromPromise(promise);
    }

    @action.bound
    public logout() {
        this.authUser?.signOut();
        this.authState = AuthState.Initialized;
        this.authUser = undefined;
    }
}
