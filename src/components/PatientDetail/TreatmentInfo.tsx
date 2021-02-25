import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Grid } from '@material-ui/core';
import EditIcon from '@material-ui/icons/Edit';
import { action, observable } from 'mobx';
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
import { ITreatmentInfo } from 'src/services/types';
import { useStores } from 'src/stores/stores';

interface ITreatmentInfoContentProps extends Partial<ITreatmentInfo> {
    editable?: boolean;
    onValueChange: (key: string, value: any) => void;
}

const TreatmentInfoContent: FunctionComponent<ITreatmentInfoContentProps> = (props) => {
    const {
        editable,
        treatmentStatus,
        followupSchedule,
        discussionFlag,
        referral,
        treatmentPlan,
        onValueChange,
    } = props;

    return (
        <Grid container spacing={2} alignItems="stretch">
            <GridDropdownField
                editable={editable}
                label="Treatment Status"
                value={treatmentStatus}
                options={treatmentStatusValues}
                onChange={(text) => onValueChange('treatmentStatus', text)}
            />
            <GridDropdownField
                editable={editable}
                label="Follow-up Schedule"
                value={followupSchedule}
                options={followupScheduleValues}
                onChange={(text) => onValueChange('followupSchedule', text)}
            />
            <GridDropdownField
                editable={editable}
                label="Flag for Discussion"
                value={discussionFlag}
                options={discussionFlagValues}
                onChange={(text) => onValueChange('discussionFlag', text)}
            />
            <GridDropdownField
                editable={editable}
                label="Referrals"
                value={referral}
                options={referralValues}
                onChange={(text) => onValueChange('referral', text)}
            />

            <GridTextField
                fullWidth={true}
                editable={editable}
                multiline={true}
                maxLine={4}
                label="Treatment Plan"
                value={treatmentPlan}
                onChange={(text) => onValueChange('treatmentPlan', text)}
            />
        </Grid>
    );
};

const state = observable<{ open: boolean } & ITreatmentInfo>({
    open: false,
    treatmentStatus: 'Active',
    followupSchedule: '2-week follow-up',
    discussionFlag: 'None',
    referral: 'None',
    treatmentPlan: '',
});

export const TreatmentInfo: FunctionComponent = observer(() => {
    const { currentPatient } = useStores();
    const onValueChange = action((key: string, value: any) => {
        (state as any)[key] = value;
    });

    const handleClose = action(() => {
        state.open = false;
    });

    const handleOpen = action(() => {
        if (!!currentPatient) {
            state.treatmentStatus = currentPatient.treatmentStatus;
            state.followupSchedule = currentPatient.followupSchedule;
            state.discussionFlag = currentPatient.discussionFlag;
            state.referral = currentPatient.referral;
            state.treatmentPlan = currentPatient.treatmentPlan;
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
            id="treatment"
            title="Treatment Information"
            actionButtons={[{ icon: <EditIcon />, text: 'Edit', onClick: handleOpen } as IActionButton]}>
            <TreatmentInfoContent
                editable={false}
                treatmentStatus={currentPatient?.treatmentStatus}
                followupSchedule={currentPatient?.followupSchedule}
                discussionFlag={currentPatient?.discussionFlag}
                referral={currentPatient?.referral}
                treatmentPlan={currentPatient?.treatmentPlan}
                onValueChange={onValueChange}
            />

            <Dialog open={state.open} onClose={handleClose}>
                <DialogTitle>Edit Treatment Information</DialogTitle>
                <DialogContent>
                    <TreatmentInfoContent editable={true} {...state} onValueChange={onValueChange} />
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

export default TreatmentInfo;
