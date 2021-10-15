import { Grid } from '@material-ui/core';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import AssessmentProgress from 'src/components/PatientDetail/AssessmentProgress';
import { IAssessmentContent, KeyedMap } from 'src/services/types';
import { usePatient, useStores } from 'src/stores/stores';

export const ProgressInformation: FunctionComponent = observer(() => {
    const {
        appConfig: { assessments },
    } = useStores();

    const currentPatient = usePatient();

    const validAssessments = assessments.reduce(
        (prev, curr) => ({ ...prev, [curr.name]: curr }),
        {}
    ) as KeyedMap<IAssessmentContent>;
    const validAssessmentNames = Object.keys(validAssessments);

    return (
        <Grid container spacing={3} alignItems="stretch" direction="row">
            {validAssessmentNames.map((assessmentName) => {
                const assessmentContent = validAssessments[assessmentName];
                const assessmentMax = Math.max(...assessmentContent.options.map((o) => o.value));
                const assessmentData = currentPatient?.assessments.find((a) => a.assessmentType == assessmentName);
                return (
                    <Grid item xs={12} sm={12} key={assessmentName}>
                        <AssessmentProgress
                            assessmentType={assessmentName}
                            assessment={assessmentData}
                            instruction={assessmentContent.instruction}
                            questions={assessmentContent.questions}
                            options={assessmentContent.options}
                            maxValue={assessmentMax}
                        />
                    </Grid>
                );
            })}
        </Grid>
    );
});

export default ProgressInformation;
