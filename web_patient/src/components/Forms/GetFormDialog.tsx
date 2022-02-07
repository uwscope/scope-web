import React, { FunctionComponent } from 'react';
import { ActivityLoggingForm } from 'src/components/Forms/ActivityLoggingForm';
import AddEditActivityForm from 'src/components/Forms/AddEditActivityForm';
import { AssessmentForm } from 'src/components/Forms/AssessmentForm';
import MoodLoggingForm from 'src/components/Forms/MoodLoggingForm';
import SafetyPlanForm from 'src/components/Forms/SafetyPlanForm';
import { getRouteParameter, Parameters, ParameterValues } from 'src/services/routes';

const formComponents: { [paramName: string]: FunctionComponent<IFormProps> } = {
    [ParameterValues.form.moodLog]: MoodLoggingForm,
    [ParameterValues.form.assessmentLog]: AssessmentForm,
    [ParameterValues.form.activityLog]: ActivityLoggingForm,
    [ParameterValues.form.addActivity]: AddEditActivityForm,
    [ParameterValues.form.editActivity]: AddEditActivityForm,
    [ParameterValues.form.safetyPlan]: SafetyPlanForm,
};

export interface IFormProps {}

export default () => {
    const formName = getRouteParameter(Parameters.form);

    if (!!formName) {
        const Component = formComponents[formName];

        if (!!Component) {
            return <Component />;
        }
    }

    return null;
};
