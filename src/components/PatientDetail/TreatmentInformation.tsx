import { Grid } from '@material-ui/core';
import EditIcon from '@material-ui/icons/Edit';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel, { IActionButton } from '../common/ActionPanel';
import { GridDropdownField, GridTextField } from '../common/GridField';

export interface ITreatmentInformationProps {
    editable?: boolean;
}

export const TreatmentInformation: FunctionComponent<ITreatmentInformationProps> = observer((props) => {
    const { editable } = props;
    return (
        <ActionPanel
            title="Treatment Information"
            actionButtons={[{ icon: <EditIcon />, text: 'Edit' } as IActionButton]}>
            <Grid container spacing={2} alignItems="stretch">
                <GridDropdownField
                    editable={editable}
                    label="Treatment Status"
                    defaultValue="1"
                    options={['1', '2', '3']}
                />
                <GridDropdownField
                    editable={editable}
                    label="Follow-up Schedule"
                    defaultValue="1"
                    options={['1', '2', '3']}
                />
                <GridDropdownField
                    editable={editable}
                    label="Flag for Discussion"
                    defaultValue="1"
                    options={['1', '2', '3']}
                />
                <GridDropdownField editable={editable} label="Referrals" defaultValue="1" options={['1', '2', '3']} />

                <GridTextField
                    fullWidth={true}
                    editable={editable}
                    multiline={true}
                    maxLine={4}
                    label="Treatment Plan"
                    defaultValue="None"
                />
            </Grid>
        </ActionPanel>
    );
});

export default TreatmentInformation;
