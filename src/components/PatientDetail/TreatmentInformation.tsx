import { Grid, Typography } from '@material-ui/core';
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
import { useStores } from 'src/stores/stores';

export interface ITreatmentInformationProps {
    editable?: boolean;
}

export const TreatmentInformation: FunctionComponent<ITreatmentInformationProps> = observer((props) => {
    const { editable } = props;
    const { currentPatient } = useStores();

    if (!!currentPatient) {
        return (
            <ActionPanel
                id="treatment"
                title="Treatment Information"
                actionButtons={[{ icon: <EditIcon />, text: 'Edit' } as IActionButton]}>
                <Grid container spacing={2} alignItems="stretch">
                    <GridDropdownField
                        editable={editable}
                        label="Treatment Status"
                        value={currentPatient.treatmentStatus}
                        options={treatmentStatusValues}
                    />
                    <GridDropdownField
                        editable={editable}
                        label="Follow-up Schedule"
                        value={currentPatient.followupSchedule}
                        options={followupScheduleValues}
                    />
                    <GridDropdownField
                        editable={editable}
                        label="Flag for Discussion"
                        value={currentPatient.discussionFlag}
                        options={discussionFlagValues}
                    />
                    <GridDropdownField
                        editable={editable}
                        label="Referrals"
                        value={currentPatient.referral}
                        options={referralValues}
                    />

                    <GridTextField
                        fullWidth={true}
                        editable={editable}
                        multiline={true}
                        maxLine={4}
                        label="Treatment Plan"
                        value={currentPatient.treatmentPlan}
                    />
                </Grid>
            </ActionPanel>
        );
    } else {
        return <Typography variant="h1">Error</Typography>;
    }
});

export default TreatmentInformation;
