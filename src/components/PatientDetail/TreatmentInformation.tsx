import { Grid } from '@material-ui/core';
import EditIcon from '@material-ui/icons/Edit';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { GridDropdownField, GridTextField } from 'src/components/common/GridField';
import {
    discussionFlagValues,
    followupScheduleValues,
    referralValues,
    treatmentStatusValues,
} from 'src/services/enums';

export interface ITreatmentInformationProps {
    editable?: boolean;
}

export const TreatmentInformation: FunctionComponent<ITreatmentInformationProps> = observer((props) => {
    const { editable } = props;
    return (
        <ActionPanel
            id="treatment"
            title="Treatment Information"
            actionButtons={[{ icon: <EditIcon />, text: 'Edit' } as IActionButton]}>
            <Grid container spacing={2} alignItems="stretch">
                <GridDropdownField
                    editable={editable}
                    label="Treatment Status"
                    defaultValue="Active Distressed"
                    options={treatmentStatusValues}
                />
                <GridDropdownField
                    editable={editable}
                    label="Follow-up Schedule"
                    defaultValue="2-week follow-up"
                    options={followupScheduleValues}
                />
                <GridDropdownField
                    editable={editable}
                    label="Flag for Discussion"
                    defaultValue="Flag as safety risk"
                    options={discussionFlagValues}
                />
                <GridDropdownField
                    editable={editable}
                    label="Referrals"
                    defaultValue="Pt Navigation"
                    options={referralValues}
                />

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
