import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { BrowserRouter, Route, Switch as RouterSwitch } from 'react-router-dom';
import CaseloadPage from './components/CaseloadPage';
import Chrome from './components/Chrome';
import DrawerContent from './components/DrawerContent';
import HeaderContent from './components/HeaderContent';
import HomePage from './components/HomePage';

export const App: FunctionComponent = observer(() => {
    return (
        <BrowserRouter>
            <Chrome drawerContent={<DrawerContent />} headerContent={<HeaderContent />}>
                <RouterSwitch>
                    <Route path="/caseload">
                        <CaseloadPage />
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
