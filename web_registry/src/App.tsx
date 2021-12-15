import { observer } from 'mobx-react-lite';
import React, { FunctionComponent } from 'react';
import { BrowserRouter, Route, Switch as RouterSwitch } from 'react-router-dom';
import CaseloadPage from 'src/components/caseload/CaseloadPage';
import Chrome from 'src/components/chrome/Chrome';
import HeaderContent from 'src/components/chrome/HeaderContent';
import Login from 'src/components/login/Login';
import PatientDetailPage from 'src/components/PatientDetail/PatientDetailPage';
import { AuthState } from 'src/stores/AuthStore';
import { useStores } from 'src/stores/stores';

export const App: FunctionComponent = observer(() => {
    const { authStore } = useStores();
    if (authStore.authState != AuthState.Authenticated) {
        return <Login />;
    }

    return (
        <BrowserRouter>
            <Chrome headerContent={<HeaderContent />}>
                <RouterSwitch>
                    <Route path="/patient/:recordId">
                        <PatientDetailPage />
                    </Route>
                    {/* Leave default route to last */}
                    <Route path="/">
                        <CaseloadPage />
                    </Route>
                </RouterSwitch>
            </Chrome>
        </BrowserRouter>
    );
});

export default App;
