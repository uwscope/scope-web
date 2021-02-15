import { Grid, Typography } from '@material-ui/core';
import EditIcon from '@material-ui/icons/Edit';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { GridTextField } from 'src/components/common/GridField';
import { useStores } from 'src/stores/stores';

export interface IPsychiatryInformationProps {
    editable?: boolean;
}

export const PsychiatryInformation: FunctionComponent<IPsychiatryInformationProps> = observer((props) => {
    const { editable } = props;
    const { currentPatient } = useStores();

    if (!!currentPatient) {
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
                        value={currentPatient.psychHistory}
                    />
                    <GridTextField
                        fullWidth={true}
                        editable={editable}
                        multiline={true}
                        maxLine={5}
                        label="Substance Use"
                        value={currentPatient.substanceUse}
                    />
                    <GridTextField
                        fullWidth={true}
                        editable={editable}
                        multiline={true}
                        maxLine={5}
                        label="Psychiatric Medications"
                        value={currentPatient.psychMedications}
                    />
                    <GridTextField
                        fullWidth={true}
                        editable={editable}
                        multiline={true}
                        maxLine={5}
                        label="Psychiatric Diagnosis"
                        value={currentPatient.psychDiagnosis}
                    />
                </Grid>
            </ActionPanel>
        );
    } else {
        return <Typography variant="h1">Error</Typography>;
    }
});

export default PsychiatryInformation;
