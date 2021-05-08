import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Grid } from '@material-ui/core';
import EditIcon from '@material-ui/icons/Edit';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { GridTextField } from 'src/components/common/GridField';
import { IClinicalHistory } from 'src/services/types';
import { usePatient } from 'src/stores/stores';

interface IClinicalHistoryContentProps extends Partial<IClinicalHistory> {
    editable?: boolean;
    onValueChange: (key: string, value: any) => void;
}

const ClinicalHistoryContent: FunctionComponent<IClinicalHistoryContentProps> = (props) => {
    const { editable, primaryCancerDiagnosis, pastPsychHistory, pastSubstanceUse, onValueChange } = props;

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
                maxLine={5}
                label="Past Psychiatric History (Include prior diagnosis, treatment, hospitalization, and suicide attempts)"
                value={pastPsychHistory}
                onChange={(text) => onValueChange('pastPsychHistory', text)}
            />
            <GridTextField
                sm={12}
                editable={editable}
                multiline={true}
                maxLine={5}
                label="Substance Use History"
                value={pastSubstanceUse}
                onChange={(text) => onValueChange('pastSubstanceUse', text)}
            />
        </Grid>
    );
};

const state = observable<{ open: boolean } & IClinicalHistory>({
    open: false,
    primaryCancerDiagnosis: '',
    pastPsychHistory: '',
    pastSubstanceUse: '',
});

export const ClinicalHistory: FunctionComponent = observer(() => {
    const currentPatient = usePatient();

    const onValueChange = action((key: string, value: any) => {
        (state as any)[key] = value;
    });

    const handleClose = action(() => {
        state.open = false;
    });

    const handleOpen = action(() => {
        if (!!currentPatient) {
            state.primaryCancerDiagnosis = currentPatient.primaryCancerDiagnosis;
            state.pastPsychHistory = currentPatient.pastPsychHistory;
            state.pastSubstanceUse = currentPatient.pastSubstanceUse;
        }

        state.open = true;
    });

    const onSave = action(() => {
        const { open, ...patientData } = { ...state };
        currentPatient?.updatePatientData(patientData);
        state.open = false;
    });

    return (
        <ActionPanel
            id="clinical-history"
            title="Clinical History"
            loading={currentPatient?.state == 'Pending'}
            actionButtons={[{ icon: <EditIcon />, text: 'Edit', onClick: handleOpen } as IActionButton]}>
            <ClinicalHistoryContent
                editable={false}
                primaryCancerDiagnosis={currentPatient?.primaryCancerDiagnosis}
                pastPsychHistory={currentPatient?.pastPsychHistory}
                pastSubstanceUse={currentPatient?.pastSubstanceUse}
                onValueChange={onValueChange}
            />

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
