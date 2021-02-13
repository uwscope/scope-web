import { Grid } from '@material-ui/core';
import EditIcon from '@material-ui/icons/Edit';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { GridTextField } from 'src/components/common/GridField';

export interface IPsychiatryInformationProps {
    editable?: boolean;
}

export const PsychiatryInformation: FunctionComponent<IPsychiatryInformationProps> = observer((props) => {
    const { editable } = props;
    return (
        <ActionPanel
            id="psychiatry"
            title="Psychiatry Information"
            actionButtons={[{ icon: <EditIcon />, text: 'Edit' } as IActionButton]}>
            <Grid container spacing={2} alignItems="stretch">
                <GridTextField
                    fullWidth={true}
                    editable={editable}
                    multiline={true}
                    maxLine={5}
                    label="Psychiatric History"
                    defaultValue="None"
                />
                <GridTextField
                    fullWidth={true}
                    editable={editable}
                    multiline={true}
                    maxLine={5}
                    label="Substance Use"
                    defaultValue="None"
                />
                <GridTextField
                    fullWidth={true}
                    editable={editable}
                    multiline={true}
                    maxLine={5}
                    label="Psychiatric Medications"
                    defaultValue="None"
                />
                <GridTextField
                    fullWidth={true}
                    editable={editable}
                    multiline={true}
                    maxLine={5}
                    label="Psychiatric Diagnosis"
                    defaultValue="None"
                />
            </Grid>
        </ActionPanel>
    );
});

export default PsychiatryInformation;
