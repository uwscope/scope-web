import React, { FunctionComponent } from 'react';
import { BrowserRouter, Route, Switch as RouterSwitch } from 'react-router-dom';
import CaseloadPage from 'src/components/caseload/CaseloadPage';
import Chrome from 'src/components/chrome/Chrome';
import HeaderContent from 'src/components/chrome/HeaderContent';
import PatientDetailPage from 'src/components/PatientDetail/PatientDetailPage';
import AppHost from 'src/components/chrome/AppHost';

export const App: FunctionComponent = () => {
    return (
        <AppHost>
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
        </AppHost>
    );
};

export default App;
