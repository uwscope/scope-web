import { IUser } from "./types";

export interface IAuthService {
    // TODO: async/await: Need babel polyfill
    login(): IUser; //Promise<IUser>;
}

class AuthService implements IAuthService {

    public login() {
        const user = {
            name: 'Luke Skywalker',
            authToken: 'my token'
        } as IUser;

        return user; //Promise.resolve(user);
    }
}

export const AuthServiceInstance = new AuthService() as IAuthService;
