import { Grid } from '@material-ui/core';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActivityProgress from 'src/components/PatientDetail/ActivityProgress';
import AssessmentProgress from 'src/components/PatientDetail/AssessmentProgress';
import MedicationProgress from 'src/components/PatientDetail/MedicationProgress';
import MoodProgress from 'src/components/PatientDetail/MoodProgress';
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

    const getProgress = (assessmentName: string) => {
        const assessmentContent = validAssessments[assessmentName];
        const assessmentMax = Math.max(...assessmentContent.options.map((o) => o.value));
        const assessmentData = currentPatient?.assessments.find((a) => a.assessmentType == assessmentName);

        if (!!assessmentData) {
            switch (assessmentName) {
                case 'PHQ-9':
                case 'GAD-7':
                    return (
                        <Grid item xs={12} sm={12} key={assessmentName}>
                            <AssessmentProgress
                                assessment={assessmentData}
                                instruction={assessmentContent.instruction}
                                questions={assessmentContent.questions}
                                options={assessmentContent.options}
                                maxValue={assessmentMax}
                                canAdd={true}
                            />
                        </Grid>
                    );
                case 'Mood Logging':
                    return (
                        <Grid item xs={12} sm={12} key={assessmentName}>
                            <MoodProgress
                                assessmentType={assessmentName}
                                maxValue={assessmentMax}
                                moodLogs={assessmentData?.data || []}
                            />
                        </Grid>
                    );
                case 'Medication Tracking':
                    return (
                        <Grid item xs={12} sm={12} key={assessmentName}>
                            <MedicationProgress assessment={assessmentData} />
                        </Grid>
                    );
            }
        }
    };

    return (
        <Grid container spacing={3} alignItems="stretch" direction="row">
            {validAssessmentNames.map(getProgress)}
            <Grid item xs={12} sm={12}>
                <ActivityProgress />
            </Grid>
        </Grid>
    );
});

export default ProgressInformation;
