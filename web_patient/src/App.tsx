import React, { FunctionComponent } from 'react';
import { BrowserRouter, Route, Routes as RouterSwitch } from 'react-router-dom';
import CarePlanPage from 'src/components/CarePlan/CarePlanPage';
import AppHost from 'src/components/Chrome/AppHost';
import Chrome from 'src/components/Chrome/Chrome';
import HomePage from 'src/components/Home/HomePage';
import ActivityTrackingHome from 'src/components/Progress/ActivityTrackingHome';
import AssessmentHome from 'src/components/Progress/AssessmentHome';
import MoodTrackingHome from 'src/components/Progress/MoodTrackingHome';
import ProgressPage from 'src/components/Progress/ProgressPage';
import AboutUsPage from 'src/components/Resources/AboutUsPage';
import CrisisResourcesPage from 'src/components/Resources/CrisisResourcesPage';
import ResourcesPage from 'src/components/Resources/ResourcesPage';
import LifeAreaDetail from 'src/components/ValuesInventory/LifeAreaDetail';
import ValuesInventoryHome from 'src/components/ValuesInventory/ValuesInventoryHome';
import WorksheetsHome from 'src/components/Worksheets/WorksheetsHome';
import { Routes } from 'src/services/routes';

export const App: FunctionComponent = () => {
    return (
        <AppHost>
            <BrowserRouter>
                <Chrome>
                    <RouterSwitch>
                        <Route
                            path={`/${Routes.resources}/*`}
                            element={
                                <RouterSwitch>
                                    <Route
                                        path={`/${Routes.valuesInventory}/:lifeareaId`}
                                        element={<LifeAreaDetail />}
                                    />
                                    <Route path={`/${Routes.valuesInventory}`} element={<ValuesInventoryHome />} />
                                    <Route path={`/${Routes.worksheets}`} element={<WorksheetsHome />} />
                                    <Route path={`/${Routes.aboutus}`} element={<AboutUsPage />} />
                                    <Route path={`/${Routes.crisisresources}`} element={<CrisisResourcesPage />} />
                                    <Route path="/" element={<ResourcesPage />} />
                                </RouterSwitch>
                            }
                        />
                        <Route
                            path={`/${Routes.progress}/*`}
                            element={
                                <RouterSwitch>
                                    <Route path={`/${Routes.moodProgress}`} element={<MoodTrackingHome />} />
                                    <Route path={`/${Routes.activityProgress}`} element={<ActivityTrackingHome />} />
                                    <Route
                                        path={`/${Routes.phqProgress}`}
                                        element={<AssessmentHome assessmentType="phq-9" />}
                                    />
                                    <Route
                                        path={`/${Routes.gadProgress}`}
                                        element={<AssessmentHome assessmentType="gad-7" />}
                                    />
                                    <Route path="/" element={<ProgressPage />} />
                                </RouterSwitch>
                            }
                        />
                        <Route path={`/${Routes.careplan}`} element={<CarePlanPage />} />
                        <Route path="/" element={<HomePage />} />
                    </RouterSwitch>
                </Chrome>
            </BrowserRouter>
        </AppHost>
    );
};

export default App;
