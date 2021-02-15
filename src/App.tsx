import React, { FunctionComponent } from 'react';
import { BrowserRouter, Route, Switch as RouterSwitch } from 'react-router-dom';
import CaseloadPage from './components/caseload/CaseloadPage';
import Chrome from './components/chrome/Chrome';
import DrawerContent from './components/chrome/DrawerContent';
import HeaderContent from './components/chrome/HeaderContent';
import HomePage from './components/home/HomePage';
import PatientDetailPage from './components/PatientDetail/PatientDetailPage';

export const App: FunctionComponent = () => {
    return (
        <BrowserRouter>
            <Chrome drawerContent={<DrawerContent />} headerContent={<HeaderContent />}>
                <RouterSwitch>
                    <Route path="/caseload">
                        <CaseloadPage />
                    </Route>
                    <Route path="/patient/:mrn">
                        <PatientDetailPage />
                    </Route>
                    {/* Leave default route to last */}
                    <Route path="/">
                        <HomePage />
                    </Route>
                </RouterSwitch>
            </Chrome>
        </BrowserRouter>
    );
};

export default App;
