import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Grid } from '@material-ui/core';
import EditIcon from '@material-ui/icons/Edit';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { IClinicalHistory } from 'shared/types';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { GridMultiSelectField, GridTextField } from 'src/components/common/GridField';
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
                flags={currentTreatmentRegimen}
                other={currentTreatmentRegimenOther}
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

const defaultTreatmentRegimen = {
    Surgery: false,
    Chemotherapy: false,
    Radiation: false,
    'Stem Cell Transplant': false,
    Immunotherapy: false,
    'CAR-T': false,
    Endocrine: false,
    Surveillance: false,
    Other: false,
};

const state = observable<{ open: boolean } & IClinicalHistory>({
    open: false,
    primaryCancerDiagnosis: '',
    currentTreatmentRegimen: defaultTreatmentRegimen,
    currentTreatmentRegimenOther: '',
    currentTreatmentRegimenNotes: '',
    dateOfCancerDiagnosis: '',
    psychDiagnosis: '',
    pastPsychHistory: '',
    pastSubstanceUse: '',
    psychSocialBackground: '',
});

export const ClinicalHistory: FunctionComponent = observer(() => {
    const currentPatient = usePatient();
    const { clinicalHistory } = currentPatient;

    const onValueChange = action((key: string, value: any) => {
        (state as any)[key] = value;
    });

    const handleClose = action(() => {
        state.open = false;
    });

    const handleOpen = action(() => {
        if (!!currentPatient) {
            Object.assign(state, clinicalHistory);
        }

        state.open = true;
    });

    const onSave = action(() => {
        const { open, ...patientData } = { ...state };
        currentPatient?.updateClinicalHistory(patientData);
        state.open = false;
    });

    return (
        <ActionPanel
            id="clinical-history"
            title="Clinical History and Diagnosis"
            loading={currentPatient?.state == 'Pending'}
            actionButtons={[{ icon: <EditIcon />, text: 'Edit', onClick: handleOpen } as IActionButton]}>
            <ClinicalHistoryContent editable={false} {...clinicalHistory} onValueChange={onValueChange} />

            <Dialog open={state.open} onClose={handleClose}>
                <DialogTitle>Edit Clinical History</DialogTitle>
                <DialogContent>
                    <ClinicalHistoryContent editable={true} {...state} onValueChange={onValueChange} />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose} color="primary">
                        Cancel
                    </Button>
                    <Button onClick={onSave} color="primary">
                        Save
                    </Button>
                </DialogActions>
            </Dialog>
        </ActionPanel>
    );
});

export default ClinicalHistory;
