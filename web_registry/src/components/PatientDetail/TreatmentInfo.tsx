import { Grid } from '@mui/material';
import { compareDesc, format } from 'date-fns';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { BehavioralStrategyChecklistFlags, BehavioralStrategyChecklistItem } from 'shared/enums';
import { formatDateOnly } from 'shared/time';
import ActionPanel from 'src/components/common/ActionPanel';
import { GridTextField } from 'src/components/common/GridField';
import { usePatient } from 'src/stores/stores';
import { getLatestScore } from 'src/utils/assessment';

export const TreatmentInfo: FunctionComponent = observer(() => {
    const currentPatient = usePatient();

    const sortedAssessmentLogs = currentPatient?.assessmentLogs
        .slice()
        .sort((a, b) => compareDesc(a.recordedDateTime, b.recordedDateTime));

    const latestPhqLog = sortedAssessmentLogs.filter((a) => a.assessmentId == 'phq-9')[0];
    const latestPhqScore = getLatestScore(currentPatient?.assessmentLogs, 'phq-9');
    const latestGadLog = sortedAssessmentLogs.filter((a) => a.assessmentId == 'gad-7')[0];
    const latestGadScore = getLatestScore(currentPatient?.assessmentLogs, 'gad-7');

    const latestSessionDate = currentPatient.latestSession?.date;
    const currentMedications = currentPatient.latestSession?.currentMedications;
    const behavioralStrategiesUsedFlags: BehavioralStrategyChecklistFlags = {
        'Behavioral Activation': false,
        'Motivational Interviewing': false,
        'Problem Solving Therapy': false,
        'Cognitive Therapy': false,
        'Mindfulness Strategies': false,
        'Supportive Therapy': false,
        Other: false,
    };

    currentPatient.sessions.forEach((s) => {
        Object.keys(s.behavioralStrategyChecklist).forEach((k) => {
            if (!!s.behavioralStrategyChecklist[k as BehavioralStrategyChecklistItem]) {
                behavioralStrategiesUsedFlags[k as BehavioralStrategyChecklistItem] = true;
            }
        });
    });

    const behavioralStrategiesUsedList: string[] = [];
    Object.keys(behavioralStrategiesUsedFlags).forEach((k) => {
        if (!!behavioralStrategiesUsedFlags[k as BehavioralStrategyChecklistItem]) {
            behavioralStrategiesUsedList.push(k);
        }
    });

    const behavioralStrategiesUsed = behavioralStrategiesUsedList.join('\n');

    const referrals = currentPatient.latestSession?.referrals
        .map((ref) => `${ref.referralType} - ${ref.referralStatus}`)
        .join('\n');

    const loading =
        currentPatient?.loadPatientState.pending ||
        currentPatient?.loadSessionsState.pending ||
        currentPatient?.loadAssessmentLogsState.pending;
    const error = currentPatient?.loadSessionsState.error || currentPatient?.loadAssessmentLogsState.error;

    return (
        <ActionPanel id="treatment" title="Ongoing Treatment Information" loading={loading} error={error}>
            <Grid container spacing={2} alignItems="stretch">
                <GridTextField
                    sm={6}
                    label="Latest PHQ-9 Score"
                    value={latestPhqScore > 0 ? latestPhqScore : 'No data'}
                    helperText={
                        !!latestPhqLog ? `Updated: ${format(latestPhqLog.recordedDateTime, 'MM/dd/yyyy')}` : undefined
                    }
                />
                <GridTextField
                    sm={6}
                    label="Latest GAD-7 Score"
                    value={latestGadScore > 0 ? latestGadScore : 'No data'}
                    helperText={
                        !!latestGadLog ? `Updated: ${format(latestGadLog.recordedDateTime, 'MM/dd/yyyy')}` : undefined
                    }
                />
                <GridTextField
                    sm={12}
                    label="Current medications"
                    value={currentMedications}
                    multiline={true}
                    helperText={
                        !!latestSessionDate ? `Updated: ${formatDateOnly(latestSessionDate, 'MM/dd/yyyy')}` : undefined
                    }
                />
                <GridTextField
                    sm={12}
                    label="Behavioral Strategies Used"
                    value={behavioralStrategiesUsed}
                    multiline={true}
                    helperText={
                        !!latestSessionDate ? `Updated: ${formatDateOnly(latestSessionDate, 'MM/dd/yyyy')}` : undefined
                    }
                />
                <GridTextField
                    sm={12}
                    label="Referrals"
                    value={referrals}
                    multiline={true}
                    helperText={
                        !!latestSessionDate ? `Updated: ${formatDateOnly(latestSessionDate, 'MM/dd/yyyy')}` : undefined
                    }
                />
            </Grid>
        </ActionPanel>
    );
});

export default TreatmentInfo;
