import React, { FunctionComponent } from 'react';
import { BrowserRouter, Route, Switch as RouterSwitch } from 'react-router-dom';
import CaseloadPage from './components/caseload/CaseloadPage';
import Chrome from './components/chrome/Chrome';
import HeaderContent from './components/chrome/HeaderContent';
import PatientDetailPage from './components/PatientDetail/PatientDetailPage';

export const App: FunctionComponent = () => {
    return (
        <BrowserRouter>
            <Chrome headerContent={<HeaderContent />}>
                <RouterSwitch>
                    <Route path="/patient/:mrn">
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
};

export default App;
