import { AuthenticationDetails, CognitoUser, CognitoUserPool, CognitoUserSession } from 'amazon-cognito-identity-js';
import { action, computed, makeAutoObservable, runInAction } from 'mobx';
import { IUser } from 'shared/types';
import { PromiseQuery } from 'src/services/promiseQuery';

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
    isAuthenticated: boolean;
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

    // App metadata
    public appTitle = 'SCOPE Patient app';

    // Promise queries
    private readonly authQuery: PromiseQuery<CognitoUserSession>;

    constructor() {
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

            if (idToken?.payload['sub'] && idToken?.payload['name'] && idToken?.getJwtToken()) {
                return {
                    identityId: idToken?.payload['sub'],
                    name: idToken?.payload['name'],
                    authToken: idToken?.getJwtToken(),
                };
            }
        }

        // Pretend authentication worked
        return {
            identityId: '7ja2mhl5py',
            name: 'Fake User',
            authToken: 'fake auth token',
        };
        // return undefined;
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
                    runInAction(() => {
                        this.authUser = authUser;
                        this.authData = undefined;
                        this.authState = AuthState.Authenticated;
                    });
                    resolve(data);
                }),
                onFailure: action((err) => {
                    console.error('onLoginFailure: ', err);
                    runInAction(() => {
                        this.authUser = undefined;
                        this.authData = undefined;

                        // Pretend login worked
                        this.authState = AuthState.Authenticated;
                        // this.authState = AuthState.AuthenticationFailed;
                    });
                    reject(err);
                }),
                newPasswordRequired: action((data: CognitoUser) => {
                    console.log('newPasswordRequired: ', data);
                    runInAction(() => {
                        this.authUser = authUser;
                        this.authData = data;
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
            this.authUser?.completeNewPasswordChallenge(password, this.authData, {
                onSuccess: action((data) => {
                    console.log('onUpdateSuccess: ', data);
                    runInAction(() => {
                        this.authData = undefined;
                        this.authState = AuthState.Authenticated;
                    });
                    console.log('authdata', this.authData);
                    resolve(data);
                }),
                onFailure: action((err) => {
                    console.error('onUpdateFailure: ', err);
                    runInAction(() => {
                        this.authUser = undefined;
                        this.authData = undefined;
                        this.authState = AuthState.AuthenticationFailed;
                    });
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
