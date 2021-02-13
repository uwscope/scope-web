import { Grid } from '@material-ui/core';
import EditIcon from '@material-ui/icons/Edit';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { clinicCodeValues, treatmentRegimenValues } from '../../services/enums';
import ActionPanel, { IActionButton } from '../common/ActionPanel';
import { GridDropdownField, GridTextField } from '../common/GridField';

export interface IMedicalInformationProps {
    editable?: boolean;
}

export const MedicalInformation: FunctionComponent<IMedicalInformationProps> = observer((props) => {
    const { editable } = props;
    return (
        <ActionPanel
            id="medical"
            title="Medical Information"
            actionButtons={[{ icon: <EditIcon />, text: 'Edit' } as IActionButton]}>
            <Grid container spacing={2} alignItems="stretch">
                <GridTextField editable={editable} label="MRN" defaultValue="1234567890" />
                <GridTextField editable={editable} label="Sex" defaultValue="Male" />
                <GridTextField editable={editable} label="Date of Birth" defaultValue="1/2/1987" />
                <GridTextField editable={editable} label="Age" defaultValue="30" />
                <GridDropdownField
                    editable={editable}
                    label="Clinic code"
                    defaultValue="GI"
                    options={clinicCodeValues}
                />
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
        </ActionPanel>
    );
});

export default MedicalInformation;
