import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Grid, Typography } from '@material-ui/core';
import EditIcon from '@material-ui/icons/Edit';
import { format } from 'date-fns';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { GridDropdownField, GridTextField } from 'src/components/common/GridField';
import { clinicCodeValues, patientSexValues, treatmentRegimenValues } from 'src/services/enums';
import { useStores } from 'src/stores/stores';

export interface IMedicalInformationProps {
    editable?: boolean;
    loading?: boolean;
}

const MedicalInformationContent: FunctionComponent<IMedicalInformationProps> = observer((props) => {
    const { editable } = props;
    const { currentPatient } = useStores();

    if (!!currentPatient) {
        return (
            <Grid container spacing={2} alignItems="stretch">
                <GridTextField editable={editable} label="Care Manager" value={currentPatient.primaryCareManagerName} />
                <GridDropdownField
                    editable={editable}
                    label="Sex"
                    value={currentPatient.sex}
                    options={patientSexValues}
                />
                <GridTextField
                    editable={editable}
                    label="Date of Birth"
                    value={format(currentPatient.birthdate, 'MM/dd/yyyy')}
                />
                <GridTextField editable={editable} label="Age" value={currentPatient.age} />
                <GridDropdownField
                    editable={editable}
                    label="Clinic code"
                    value={currentPatient.clinicCode}
                    options={clinicCodeValues}
                />
                <GridDropdownField
                    editable={editable}
                    label="Treatment Regimen"
                    value={currentPatient.treatmentRegimen}
                    options={treatmentRegimenValues}
                />
                <GridTextField
                    fullWidth={true}
                    editable={editable}
                    multiline={true}
                    maxLine={4}
                    label="Primary Medical Diagnosis"
                    value={currentPatient.medicalDiagnosis}
                />
            </Grid>
        );
    } else {
        return <Typography variant="h1">Error</Typography>;
    }
});

const state = observable<{ open: boolean }>({
    open: false,
});

export const MedicalInformation: FunctionComponent<IMedicalInformationProps> = observer((props) => {
    const { editable, loading } = props;

    const handleClose = action(() => {
        state.open = false;
    });

    const handleOpen = action(() => {
        state.open = true;
    });

    return (
        <ActionPanel
            id="medical"
            title="Medical Information"
            loading={loading}
            actionButtons={[{ icon: <EditIcon />, text: 'Edit', onClick: handleOpen } as IActionButton]}>
            <MedicalInformationContent editable={editable} />

            <Dialog open={state.open} onClose={handleClose}>
                <DialogTitle>Edit Medical Information</DialogTitle>
                <DialogContent>
                    <MedicalInformationContent editable={true} />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose} color="primary">
                        Cancel
                    </Button>
                    <Button onClick={handleClose} color="primary">
                        Save
                    </Button>
                </DialogActions>
            </Dialog>
        </ActionPanel>
    );
});

export default MedicalInformation;
