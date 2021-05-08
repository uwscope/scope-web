import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Grid } from '@material-ui/core';
import EditIcon from '@material-ui/icons/Edit';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { GridDropdownField, GridMultiSelectField, GridTextField } from 'src/components/common/GridField';
import { followupScheduleValues } from 'src/services/enums';
import { ITreatmentInfo } from 'src/services/types';
import { usePatient } from 'src/stores/stores';

interface ITreatmentInfoContentProps extends ITreatmentInfo {
    editable?: boolean;
    onValueChange: (key: string, value: any) => void;
}

const TreatmentInfoContent: FunctionComponent<ITreatmentInfoContentProps> = (props) => {
    const {
        editable,
        currentTreatmentRegimen,
        currentTreatmentRegimenOther,
        currentTreatmentRegimenNotes,
        psychDiagnosis,
        discussionFlag,
        followupSchedule,
        onValueChange,
    } = props;

    return (
        <Grid container spacing={2} alignItems="stretch">
            <GridMultiSelectField
                editable={editable}
                label="Current Treatment Regimen"
                flags={currentTreatmentRegimen}
                other={currentTreatmentRegimenOther}
                onChange={(flags) => onValueChange('currentTreatmentRegimen', flags)}
                onOtherChange={(text) => onValueChange('currentTreatmentRegimenOther', text)}
            />
            <GridTextField
                sm={12}
                editable={editable}
                multiline={true}
                maxLine={5}
                label="Treatment Notes"
                value={currentTreatmentRegimenNotes}
                onChange={(text) => onValueChange('currentTreatmentRegimenNotes', text)}
            />
            <GridTextField
                sm={12}
                editable={editable}
                multiline={true}
                maxLine={5}
                label="Psychiatric Diagnosis"
                value={psychDiagnosis}
                onChange={(text) => onValueChange('psychDiagnosis', text)}
            />
            <GridMultiSelectField
                editable={editable}
                label="Safety and Discussion Flags"
                flags={discussionFlag}
                onChange={(flags) => onValueChange('discussionFlag', flags)}
            />
            <GridDropdownField
                editable={editable}
                label="Follow-up Schedule"
                value={followupSchedule}
                options={followupScheduleValues}
                onChange={(text) => onValueChange('followupSchedule', text)}
            />
        </Grid>
    );
};

const defaultTreatmentRegimen = {
    Surgery: false,
    Chemotherapy: false,
    Radiation: false,
    'Stem Cell Transplant': false,
    Immunotherapy: false,
    'CAR-T': false,
    Endocrine: false,
    Surveillance: false,
    Other: false,
};

const state = observable<{ open: boolean } & ITreatmentInfo>({
    open: false,
    currentTreatmentRegimen: defaultTreatmentRegimen,
    currentTreatmentRegimenOther: '',
    currentTreatmentRegimenNotes: '',
    psychDiagnosis: '',
    followupSchedule: '2-week follow-up',
    discussionFlag: { 'Flag as safety risk': false, 'Flag for discussion': false },
});

export const TreatmentInfo: FunctionComponent = observer(() => {
    const currentPatient = usePatient();

    const onValueChange = action((key: string, value: any) => {
        (state as any)[key] = value;
    });

    const handleClose = action(() => {
        state.open = false;
    });

    const handleOpen = action(() => {
        if (!!currentPatient) {
            Object.assign(state, currentPatient);
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
                currentTreatmentRegimen={currentPatient.currentTreatmentRegimen}
                currentTreatmentRegimenOther={currentPatient.currentTreatmentRegimenOther}
                currentTreatmentRegimenNotes={currentPatient.currentTreatmentRegimenNotes}
                psychDiagnosis={currentPatient.psychDiagnosis}
                discussionFlag={currentPatient.discussionFlag}
                followupSchedule={currentPatient.followupSchedule}
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
