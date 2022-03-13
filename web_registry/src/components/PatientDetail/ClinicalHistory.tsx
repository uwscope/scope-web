import EditIcon from '@mui/icons-material/Edit';
import { Grid } from '@mui/material';
import { action, runInAction } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { cancerTreatmentRegimenValues } from 'shared/enums';
import { IClinicalHistory } from 'shared/types';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { GridMultiSelectField, GridTextField } from 'src/components/common/GridField';
import StatefulDialog from 'src/components/common/StatefulDialog';
import { usePatient } from 'src/stores/stores';

interface IClinicalHistoryContentProps extends Partial<IClinicalHistory> {
    editable?: boolean;
    onValueChange: (key: string, value: any) => void;
}

const ClinicalHistoryContent: FunctionComponent<IClinicalHistoryContentProps> = (props) => {
    const {
        editable,
        primaryCancerDiagnosis,
        dateOfCancerDiagnosis,
        currentTreatmentRegimen,
        currentTreatmentRegimenOther,
        psychDiagnosis,
        currentTreatmentRegimenNotes,
        pastPsychHistory,
        pastSubstanceUse,
        psychSocialBackground,
        onValueChange,
    } = props;

    return (
        <Grid container spacing={2} alignItems="stretch">
            <GridTextField
                sm={12}
                editable={editable}
                multiline={true}
                maxLine={2}
                label="Primary Cancer Diagnosis"
                value={primaryCancerDiagnosis}
                onChange={(text) => onValueChange('primaryCancerDiagnosis', text)}
            />
            <GridTextField
                sm={12}
                editable={editable}
                multiline={true}
                maxLine={2}
                label="Date of Cancer Diagnosis"
                value={dateOfCancerDiagnosis}
                onChange={(text) => onValueChange('dateOfCancerDiagnosis', text)}
            />
            <GridMultiSelectField
                sm={12}
                editable={editable}
                label="Current Treatment Regimen"
                flags={Object.assign(
                    {},
                    ...cancerTreatmentRegimenValues.map((x) => ({ [x]: !!currentTreatmentRegimen?.[x] })),
                )}
                other={currentTreatmentRegimenOther}
                flagOrder={[...cancerTreatmentRegimenValues]}
                onChange={(flags) => onValueChange('currentTreatmentRegimen', flags)}
                onOtherChange={(text) => onValueChange('currentTreatmentRegimenOther', text)}
            />
            <GridTextField
                sm={12}
                editable={editable}
                multiline={true}
                minLine={4}
                maxLine={4}
                label="Treatment Regimen Notes"
                value={currentTreatmentRegimenNotes}
                onChange={(text) => onValueChange('currentTreatmentRegimenNotes', text)}
            />
            <GridTextField
                sm={12}
                editable={editable}
                multiline={true}
                minLine={4}
                maxLine={4}
                label="Psychiatric Diagnosis"
                value={psychDiagnosis}
                onChange={(text) => onValueChange('psychDiagnosis', text)}
            />
            <GridTextField
                sm={12}
                editable={editable}
                multiline={true}
                minLine={4}
                maxLine={4}
                label="Past Psychiatric History"
                helperText="e.g., prior diagnosis, treatment, hospitalization, and suicide attempts"
                value={pastPsychHistory}
                onChange={(text) => onValueChange('pastPsychHistory', text)}
            />
            <GridTextField
                sm={12}
                editable={editable}
                multiline={true}
                minLine={4}
                maxLine={4}
                label="Substance Use History"
                helperText="e.g., prior or current substance use"
                value={pastSubstanceUse}
                onChange={(text) => onValueChange('pastSubstanceUse', text)}
            />
            <GridTextField
                sm={12}
                editable={editable}
                multiline={true}
                minLine={4}
                maxLine={4}
                label="Psychosocial Background"
                value={psychSocialBackground}
                helperText="e.g., living situation, marital status, children, employment, trauma history"
                onChange={(text) => onValueChange('psychSocialBackground', text)}
            />
        </Grid>
    );
};

export const ClinicalHistory: FunctionComponent = observer(() => {
    const currentPatient = usePatient();
    const { clinicalHistory } = currentPatient;

    const state = useLocalObservable<{ open: boolean } & IClinicalHistory>(() => ({
        open: false,
        primaryCancerDiagnosis: clinicalHistory.primaryCancerDiagnosis || '',
        currentTreatmentRegimen: Object.assign(
            {},
            ...cancerTreatmentRegimenValues.map((x) => ({ [x]: !!clinicalHistory.currentTreatmentRegimen?.[x] })),
        ),
        currentTreatmentRegimenOther: clinicalHistory.currentTreatmentRegimenOther || '',
        currentTreatmentRegimenNotes: clinicalHistory.currentTreatmentRegimenNotes || '',
        dateOfCancerDiagnosis: clinicalHistory.dateOfCancerDiagnosis || '',
        psychDiagnosis: clinicalHistory.psychDiagnosis || '',
        pastPsychHistory: clinicalHistory.pastPsychHistory || '',
        pastSubstanceUse: clinicalHistory.pastSubstanceUse || '',
        psychSocialBackground: clinicalHistory.psychSocialBackground || '',
    }));

    const onValueChange = action((key: string, value: any) => {
        (state as any)[key] = value;
    });

    const handleClose = action(() => {
        state.open = false;

        currentPatient.loadClinicalHistoryState.resetState();
    });

    const handleOpen = action(() => {
        if (!!currentPatient) {
            Object.assign(state, clinicalHistory);
        }

        state.open = true;
    });

    const onSave = action(async () => {
        const { open, ...patientData } = { ...state };
        await currentPatient?.updateClinicalHistory(patientData);

        runInAction(() => {
            if (!currentPatient.loadClinicalHistoryState.error) {
                state.open = false;
            }
        });
    });

    return (
        <ActionPanel
            id="clinical-history"
            title="Clinical History and Diagnosis"
            error={currentPatient?.loadClinicalHistoryState.error}
            loading={currentPatient?.loadPatientState.pending || currentPatient?.loadClinicalHistoryState.pending}
            showSnackbar={!state.open}
            actionButtons={[{ icon: <EditIcon />, text: 'Edit', onClick: handleOpen } as IActionButton]}>
            <ClinicalHistoryContent editable={false} {...clinicalHistory} onValueChange={onValueChange} />

            <StatefulDialog
                open={state.open}
                error={currentPatient?.loadClinicalHistoryState.error}
                loading={currentPatient?.loadClinicalHistoryState.pending}
                handleCancel={handleClose}
                handleSave={onSave}
                title="Edit Clinical History"
                content={<ClinicalHistoryContent editable={true} {...state} onValueChange={onValueChange} />}
            />
        </ActionPanel>
    );
});

export default ClinicalHistory;
