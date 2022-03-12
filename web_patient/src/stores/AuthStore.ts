import { IPatientIdentity } from 'shared/types';
import { useServices } from 'src/services/services';
import { AuthStoreBase, IAuthStoreBase } from 'shared/authStoreBase';

export interface IAuthStore extends IAuthStoreBase<IPatientIdentity> {}

export class AuthStore extends AuthStoreBase<IPatientIdentity> implements IAuthStore {
    protected getIdentity(token: string): Promise<IPatientIdentity> {
        const { identityService } = useServices();
        return identityService.getPatientIdentity(token);
    }
}
