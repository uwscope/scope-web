import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Grid } from '@material-ui/core';
import EditIcon from '@material-ui/icons/Edit';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { GridTextField } from 'src/components/common/GridField';
import { useStores } from 'src/stores/stores';

interface IPsychiatryInfo {
    psychHistory: string;
    substanceUse: string;
    psychMedications: string;
    psychDiagnosis: string;
}

interface IPsychiatryInfoContentProps extends Partial<IPsychiatryInfo> {
    editable?: boolean;
    onValueChange: (key: string, value: any) => void;
}

const PsychiatryInformationContent: FunctionComponent<IPsychiatryInfoContentProps> = observer((props) => {
    const { editable, psychHistory, substanceUse, psychMedications, psychDiagnosis, onValueChange } = props;

    return (
        <Grid container spacing={2} alignItems="stretch">
            <GridTextField
                fullWidth={true}
                editable={editable}
                multiline={true}
                maxLine={5}
                label="Psychiatric History"
                value={psychHistory}
                onChange={(text) => onValueChange('psychHistory', text)}
            />
            <GridTextField
                fullWidth={true}
                editable={editable}
                multiline={true}
                maxLine={5}
                label="Substance Use"
                value={substanceUse}
                onChange={(text) => onValueChange('substanceUse', text)}
            />
            <GridTextField
                fullWidth={true}
                editable={editable}
                multiline={true}
                maxLine={5}
                label="Psychiatric Medications"
                value={psychMedications}
                onChange={(text) => onValueChange('psychMedications', text)}
            />
            <GridTextField
                fullWidth={true}
                editable={editable}
                multiline={true}
                maxLine={5}
                label="Psychiatric Diagnosis"
                value={psychDiagnosis}
                onChange={(text) => onValueChange('psychDiagnosis', text)}
            />
        </Grid>
    );
});

const state = observable<{ open: boolean } & IPsychiatryInfo>({
    open: false,
    psychHistory: '',
    substanceUse: '',
    psychMedications: '',
    psychDiagnosis: '',
});

export const PsychiatryInformation: FunctionComponent = observer(() => {
    const { currentPatient } = useStores();

    const onValueChange = action((key: string, value: any) => {
        (state as any)[key] = value;
    });

    const handleClose = action(() => {
        state.open = false;
    });

    const handleOpen = action(() => {
        if (!!currentPatient) {
            state.psychHistory = currentPatient.psychHistory;
            state.substanceUse = currentPatient.substanceUse;
            state.psychMedications = currentPatient.psychMedications;
            state.psychDiagnosis = currentPatient.psychDiagnosis;
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
            id="psychiatry"
            title="Psychiatry Information"
            loading={currentPatient?.state == 'Pending'}
            actionButtons={[{ icon: <EditIcon />, text: 'Edit', onClick: handleOpen } as IActionButton]}>
            <PsychiatryInformationContent
                editable={false}
                psychHistory={currentPatient?.psychHistory}
                substanceUse={currentPatient?.substanceUse}
                psychMedications={currentPatient?.psychMedications}
                psychDiagnosis={currentPatient?.psychDiagnosis}
                onValueChange={onValueChange}
            />

            <Dialog open={state.open} onClose={handleClose}>
                <DialogTitle>Edit Psychiatry Information</DialogTitle>
                <DialogContent>
                    <PsychiatryInformationContent editable={true} {...state} onValueChange={onValueChange} />
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

export default PsychiatryInformation;
