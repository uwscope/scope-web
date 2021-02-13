import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Grid } from '@material-ui/core';
import EditIcon from '@material-ui/icons/Edit';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { clinicCodeValues, treatmentRegimenValues } from '../../services/enums';
import ActionPanel, { IActionButton } from '../common/ActionPanel';
import { GridDropdownField, GridTextField } from '../common/GridField';

export interface IMedicalInformationProps {
    editable?: boolean;
    loading?: boolean;
}

const MedicalInformationContent: FunctionComponent<IMedicalInformationProps> = observer((props) => {
    const { editable } = props;
    return (
        <Grid container spacing={2} alignItems="stretch">
            <GridTextField editable={editable} label="MRN" defaultValue="1234567890" />
            <GridTextField editable={editable} label="Sex" defaultValue="Male" />
            <GridTextField editable={editable} label="Date of Birth" defaultValue="1/2/1987" />
            <GridTextField editable={editable} label="Age" defaultValue="30" />
            <GridDropdownField editable={editable} label="Clinic code" defaultValue="GI" options={clinicCodeValues} />
            <GridDropdownField
                editable={editable}
                label="Treatment Regimen"
                defaultValue="Immunotherapy"
                options={treatmentRegimenValues}
            />
            <GridTextField
                fullWidth={true}
                editable={editable}
                multiline={true}
                maxLine={4}
                label="Primary Medical Diagnosis"
                defaultValue="Lorem Ipsum"
            />
        </Grid>
    );
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
