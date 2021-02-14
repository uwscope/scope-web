import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { BrowserRouter, Route, Switch as RouterSwitch } from 'react-router-dom';
import CaseloadPage from 'src/components/CaseloadPage';
import Chrome from 'src/components/Chrome';
import DrawerContent from 'src/components/DrawerContent';
import HeaderContent from 'src/components/HeaderContent';
import HomePage from 'src/components/HomePage';
import PatientDetailPage from 'src/components/PatientDetailPage';

export const App: FunctionComponent = observer(() => {
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
});

export default App;
