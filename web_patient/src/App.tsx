import React, { FunctionComponent } from 'react';
import { Route, Routes as RouterSwitch } from 'react-router-dom';
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
                <Route path={`/${Routes.activityProgress}`} element={<ActivityTrackingHome />} />
                <Route path={`/${Routes.phqProgress}`} element={<AssessmentHome assessmentType="phq-9" />} />
                <Route path={`/${Routes.gadProgress}`} element={<AssessmentHome assessmentType="gad-7" />} />
                <Route path={`/${Routes.valuesInventory}/:lifeareaId/:valueId`} element={<ValueDetail />} />
                <Route path={`/${Routes.valuesInventory}/:lifeareaId`} element={<LifeAreaDetail />} />
                <Route path={`/${Routes.valuesInventory}`} element={<ValuesInventoryHome />} />
                <Route path={`/${Routes.resources}`} element={<ResourcesHome />} />
                <Route path={`/${Routes.careplan}`} element={<CarePlanPage />} />
                <Route path={`/${Routes.progress}`} element={<ProgressPage />} />
                <Route path={`/${Routes.profile}`} element={<ProfilePage />} />
                <Route path="/" element={<HomePage />} />
            </RouterSwitch>
        </Chrome>
    );
};

export default App;
