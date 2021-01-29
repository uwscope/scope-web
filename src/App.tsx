import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import Chrome from './components/Chrome';
import { useStores } from './stores/stores';

export const App: FunctionComponent = observer(() => {
    const rootStore = useStores();
    return (
        <Chrome>
            <div>
                <p>{rootStore.userStore.name}</p>
                {rootStore.authStore.loggedIn ? (
                    <button onClick={() => rootStore.logout()}>Logout</button>
                ) : (
                    <button onClick={() => rootStore.login()}>Login</button>
                )}
            </div>
        </Chrome>
    );
});

export default App;
