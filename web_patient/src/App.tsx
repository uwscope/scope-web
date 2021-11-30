import React, { FunctionComponent } from 'react';
import { Route, Switch as RouterSwitch } from 'react-router-dom';
import CarePlanPage from 'src/components/CarePlan/CarePlanPage';
import Chrome from 'src/components/Chrome/Chrome';
import HomePage from 'src/components/Home/HomePage';
import ProfilePage from 'src/components/Profile/ProfilePage';
import ActivityTrackingHome from 'src/components/Progress/ActivityTrackingHome';
import AssessmentHome from 'src/components/Progress/AssessmentHome';
import ProgressPage from 'src/components/Progress/ProgressPage';
import ResourcesHome from 'src/components/Resources/ResourcesHome';
import LifeAreaDetail from 'src/components/ValuesInventory/LifeAreaDetail';
import ValueDetail from 'src/components/ValuesInventory/ValueDetail';
import ValuesInventoryHome from 'src/components/ValuesInventory/ValuesInventoryHome';
import { Routes } from 'src/services/routes';

export const App: FunctionComponent = () => {
    return (
        <Chrome>
            <RouterSwitch>
                <Route path={`/${Routes.activityProgress}`}>
                    <ActivityTrackingHome />
                </Route>
                <Route path={`/${Routes.phqProgress}`}>
                    <AssessmentHome assessmentType="phq-9" />
                </Route>
                <Route path={`/${Routes.gadProgress}`}>
                    <AssessmentHome assessmentType="gad-7" />
                </Route>
                <Route path={`/${Routes.valuesInventory}/:lifeareaId/:valueId`}>
                    <ValueDetail />
                </Route>
                <Route path={`/${Routes.valuesInventory}/:lifeareaId`}>
                    <LifeAreaDetail />
                </Route>
                <Route path={`/${Routes.valuesInventory}`}>
                    <ValuesInventoryHome />
                </Route>
                <Route path={`/${Routes.resources}`}>
                    <ResourcesHome />
                </Route>
                <Route path={`/${Routes.careplan}`}>
                    <CarePlanPage />
                </Route>
                <Route path={`/${Routes.progress}`}>
                    <ProgressPage />
                </Route>
                <Route path={`/${Routes.profile}`}>
                    <ProfilePage />
                </Route>
                {/* Leave default route to last */}
                <Route path="/">
                    <HomePage />
                </Route>
            </RouterSwitch>
        </Chrome>
    );
};

export default App;
