import {
  AuthenticationDetails,
  CodeDeliveryDetails,
  CognitoRefreshToken,
  CognitoUser,
  CognitoUserPool,
  CognitoUserSession,
} from "amazon-cognito-identity-js";
import { AxiosError } from "axios";
import {
  action,
  computed,
  makeObservable,
  observable,
  runInAction,
} from "mobx";
import { getLogger } from "shared/logger";
import { PromiseQuery } from "shared/promiseQuery";
import { getLoadAndLogQuery } from "shared/stores";
import { IAppAuthConfig, IIdentity } from "shared/types";

export enum AuthState {
  Initialized,
  UpdatePasswordInProgress,
  ResetPasswordPrompt,
  ResetPasswordInProgress,
  ResetPasswordComplete,
  Authenticated,
  AuthenticationFailed,
}

export interface IAuthStoreBase<T extends IIdentity> {
  isAuthenticated: boolean;
  isAuthenticating: boolean;
  authState: AuthState;
  authStateDetail?: string;

  currentUserIdentity?: T;

  initialize: () => void;
  login(username: string, password: string): Promise<void>;
  updateTempPassword(newPassword: string): Promise<void>;
  sendResetPasswordCode(username: string): Promise<void>;
  resetPassword(resetCode: string, newPassword: string): Promise<void>;
  refreshToken(): Promise<void>;
  logout(): void;

  getToken(): string | undefined;

  clearDetail(): void;
}

const logger = getLogger("AuthStore");

export class AuthStoreBase<T extends IIdentity> implements IAuthStoreBase<T> {
  public authConfig: IAppAuthConfig;

  @observable
  public authState = AuthState.Initialized;

  @observable
  public authStateDetail?: string = undefined;

  // Promise queries
  private readonly authQuery: PromiseQuery<T>;
  private readonly sessionQuery: PromiseQuery<CognitoUserSession>;

  // This is only used to keep state for temp password change
  private authUser?: CognitoUser;

  constructor(authConfig: IAppAuthConfig) {
    this.authConfig = authConfig;

    this.authQuery = new PromiseQuery<T>(undefined, "authQuery");
    this.sessionQuery = new PromiseQuery<CognitoUserSession>(
      undefined,
      "sessionQuery",
    );

    makeObservable(this);
  }

  @computed
  public get isAuthenticated() {
    if (this.authState == AuthState.Authenticated) {
      const token = this.getToken();
      return !!this.currentUserSession && !!this.currentUserIdentity && !!token;
    }
    return false;
  }

  @computed
  public get isAuthenticating() {
    return this.authQuery.pending || this.sessionQuery.pending;
  }

  @action.bound
  public getToken() {
    if (this.authState == AuthState.Authenticated) {
      return this.currentUserSession?.getIdToken().getJwtToken();
    }

    return undefined;
  }

  @computed
  public get currentUserIdentity() {
    if (this.authState == AuthState.Authenticated) {
      return this.authQuery.value;
    }

    return undefined;
  }

  @computed
  private get currentUserSession() {
    return this.sessionQuery.value;
  }

  @action.bound
  public initialize() {
    this.authState = AuthState.Initialized;

    const lastUserName = window.localStorage.getItem(
      `CognitoIdentityServiceProvider.${this.authConfig.clientid}.LastAuthUser`,
    );

    if (!!lastUserName) {
      const authUser = new CognitoUser({
        Username: lastUserName,
        Pool: new CognitoUserPool({
          UserPoolId: this.authConfig.poolid,
          ClientId: this.authConfig.clientid,
        }),
      });

      authUser.getSession(async (_: any, session: any) => {
        if (!!session) {
          const loadAndLogQuery = getLoadAndLogQuery(logger);
          await loadAndLogQuery(
            () => this.getIdentityFromSession(Promise.resolve(session)),
            this.authQuery,
          );
        }
      });
    }
  }

  @action.bound
  public async login(username: string, password: string) {
    // Clear states
    this.authState = AuthState.Initialized;
    this.clearDetail();

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
        onSuccess: action((data: CognitoUserSession) => {
          logger.event("onLoginSuccess: ", { username });
          resolve(data);

          // Once the promise is resolved, set the correct states.
          runInAction(() => {
            this.authUser = authUser;
          });
        }),
        onFailure: action((err: any) => {
          if (err.code == "PasswordResetRequiredException") {
            logger.event("passwordResetRequired", err);
            runInAction(() => {
              this.authUser = authUser;
              this.authStateDetail = err.message;
              this.authState = AuthState.ResetPasswordInProgress;
            });
          } else {
            logger.error(err, { username });
            runInAction(() => {
              this.authUser = undefined;
              this.authStateDetail = err.message;
              this.authState = AuthState.AuthenticationFailed;
            });
          }
          reject(err);
        }),
        newPasswordRequired: action((data: any) => {
          logger.event("newPasswordRequired", data);
          runInAction(() => {
            this.authUser = authUser;
            this.authState = AuthState.UpdatePasswordInProgress;
          });
          reject("newPasswordRequired");
        }),
      });
    });

    const loadAndLogQuery = getLoadAndLogQuery(logger);
    await loadAndLogQuery(
      () => this.getIdentityFromSession(promise),
      this.authQuery,
    );
  }

  @action.bound
  public async refreshToken() {
    if (this.currentUserSession && this.currentUserSession.isValid) {
      const loadAndLogQuery = getLoadAndLogQuery(logger);
      var token = new CognitoRefreshToken({
        RefreshToken: this.currentUserSession.getRefreshToken().getToken(),
      });
      const promise = new Promise<CognitoUserSession>((resolve, reject) => {
        this.authUser?.refreshSession(
          token,
          (error: any, session: CognitoUserSession) => {
            if (error) {
              reject(error);

              // TODO: Kick user out of the app
            }

            resolve(session);
          },
        );
      });

      await loadAndLogQuery(() => promise, this.sessionQuery);
    }
  }

  @action.bound
  public async updateTempPassword(password: string) {
    // Clear states
    this.clearDetail();

    const promise = new Promise<CognitoUserSession>((resolve, reject) => {
      this.authUser?.completeNewPasswordChallenge(
        password,
        {}, // No additional required fields to set/update
        {
          onSuccess: action((data: CognitoUserSession) => {
            logger.event("onLoginSuccess", {
              username: this.authUser?.getUsername() || "unknown",
            });
            resolve(data);
          }),
          onFailure: action((err: any) => {
            logger.error(err, {
              username: this.authUser?.getUsername() || "unknown",
            });
            runInAction(() => {
              this.authStateDetail = err.message;

              this.authState =
                err.code == "NotAuthorizedException"
                  ? AuthState.AuthenticationFailed
                  : AuthState.UpdatePasswordInProgress;
            });
            reject(err);
          }),
        },
      );
    });

    const loadAndLogQuery = getLoadAndLogQuery(logger);
    await loadAndLogQuery(
      () => this.getIdentityFromSession(promise),
      this.authQuery,
    );
  }

  @action.bound
  public async sendResetPasswordCode(username: string) {
    // Clear states
    this.clearDetail();

    const authUser = new CognitoUser({
      Username: username,
      Pool: new CognitoUserPool({
        UserPoolId: this.authConfig.poolid,
        ClientId: this.authConfig.clientid,
      }),
    });

    const promise = new Promise<CognitoUserSession | undefined>(
      (resolve, reject) => {
        authUser.forgotPassword({
          onSuccess: action((data: any) => {
            const deliveryDetails =
              data.CodeDeliveryDetails as CodeDeliveryDetails;
            logger.event("onForgotPasswordSuccess", {
              ...deliveryDetails,
            });

            runInAction(() => {
              this.authUser = authUser;
              this.authState = AuthState.ResetPasswordInProgress;
            });
            resolve(undefined);
          }),
          onFailure: action((err: any) => {
            logger.error(err);
            runInAction(() => {
              this.authStateDetail = err.message;

              this.authState = AuthState.AuthenticationFailed;
            });
            reject(err);
          }),
        });
      },
    );

    const loadAndLogQuery = getLoadAndLogQuery(logger);
    await loadAndLogQuery(() => promise, this.sessionQuery);
  }

  @action.bound
  public async resetPassword(resetCode: string, password: string) {
    // Clear states
    this.clearDetail();

    const promise = new Promise<CognitoUserSession | undefined>(
      (resolve, reject) => {
        this.authUser?.confirmPassword(resetCode, password, {
          onSuccess: action((success: string) => {
            logger.event("onResetPasswordSuccess", {
              username: this.authUser?.getUsername() || "unknown",
              success,
            });

            this.authStateDetail =
              "Password reset successful. Sign in using the new password.";
            this.authState = AuthState.ResetPasswordComplete;
            resolve(undefined);
          }),
          onFailure: action((err: any) => {
            logger.error(err, {
              username: this.authUser?.getUsername() || "unknown",
            });
            runInAction(() => {
              this.authStateDetail = err.message;

              this.authState =
                err.code == "NotAuthorizedException"
                  ? AuthState.AuthenticationFailed
                  : AuthState.ResetPasswordInProgress;
            });
            reject(err);
          }),
        });
      },
    );

    const loadAndLogQuery = getLoadAndLogQuery(logger);
    await loadAndLogQuery(() => promise, this.sessionQuery);
  }

  @action.bound
  public logout() {
    window.localStorage.clear();
    this.authUser?.signOut();
    this.authState = AuthState.Initialized;
    this.authUser = undefined;

    logger.event("UserLoggedOut", { ...this.authQuery.value });
  }

  @action.bound
  public clearDetail() {
    this.authStateDetail = undefined;
  }

  private getIdentityFromSession(promise: Promise<CognitoUserSession>) {
    const identifiedPromise = this.sessionQuery
      .fromPromise(promise)
      .then(async (session) => {
        // Once the promise is resolved, get the identity

        var idToken = session?.getIdToken()?.getJwtToken();

        try {
          const identity = await this.getIdentity(idToken);

          // Temporary check for expected data
          if (!identity) {
            throw new Error("Unauthorized");
          }

          logger.event("UserLoggedIn", { name: identity.name });

          runInAction(() => {
            this.authState = AuthState.Authenticated;
          });

          return {
            ...identity,
          } as T;
        } catch (error) {
          // Password reset was successful but identity call failed
          logger.error(new Error(`${error}`));

          const axiosError = error as AxiosError;
          const myError = error as Error;
          const unauthorized =
            axiosError?.response?.status == 403 ||
            myError?.message == "Unauthorized";

          runInAction(() => {
            this.authState = AuthState.AuthenticationFailed;
            this.authStateDetail = unauthorized
              ? "Sorry, you are not authorized to access this service."
              : "Sorry, there was an issue accessing the service.";
          });
        }
      });

    return identifiedPromise;
  }

  protected getIdentity(token: string): Promise<T> {
    token;
    throw new Error("Get identity call not implemented");
  }
}
