import { IProviderIdentity } from 'shared/types';
import { useServices } from 'src/services/services';
import { AuthStoreBase, IAuthStoreBase } from 'shared/authStoreBase';

export interface IAuthStore extends IAuthStoreBase<IProviderIdentity> {}

export class AuthStore extends AuthStoreBase<IProviderIdentity> implements IAuthStore {
    protected getIdentity(token: string): Promise<IProviderIdentity> {
        const { identityService } = useServices();
        return identityService.getProviderIdentity(token);
    }
}
