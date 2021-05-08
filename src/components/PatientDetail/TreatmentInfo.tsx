import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Grid } from '@material-ui/core';
import EditIcon from '@material-ui/icons/Edit';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { GridDropdownField, GridMultiSelectField, GridTextField } from 'src/components/common/GridField';
import { depressionTreatmentStatusValues, followupScheduleValues } from 'src/services/enums';
import { ITreatmentInfo } from 'src/services/types';
import { usePatient } from 'src/stores/stores';
import { getLatestScores } from 'src/utils/assessment';

interface ITreatmentInfoContentProps extends Partial<ITreatmentInfo> {
    editable?: boolean;
    onValueChange: (key: string, value: any) => void;
    latestScores: string;
}

const TreatmentInfoContent: FunctionComponent<ITreatmentInfoContentProps> = (props) => {
    const {
        editable,
        currentTreatmentRegimen,
        currentTreatmentRegimenOther,
        depressionTreatmentStatus,
        psychDiagnosis,
        discussionFlag,
        followupSchedule,
        onValueChange,
        latestScores,
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
            <GridDropdownField
                editable={editable}
                label="Depression Treatment Status"
                value={depressionTreatmentStatus}
                options={depressionTreatmentStatusValues}
                onChange={(text) => onValueChange('depressionTreatmentStatus', text)}
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
            <GridTextField
                sm={12}
                editable={false}
                multiline={true}
                maxLine={3}
                label="Latest Assessment Scores"
                value={latestScores}
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

const state = observable<{ open: boolean; latestScores: string } & ITreatmentInfo>({
    open: false,
    currentTreatmentRegimen: defaultTreatmentRegimen,
    currentTreatmentRegimenOther: '',
    depressionTreatmentStatus: 'CoCM',
    psychDiagnosis: '',
    followupSchedule: '2-week follow-up',
    discussionFlag: { 'Flag as safety risk': false, 'Flag for discussion': false },
    latestScores: '',
});

export const TreatmentInfo: FunctionComponent = observer(() => {
    const currentPatient = usePatient();
    const latestScores = !!currentPatient ? getLatestScores(currentPatient.assessments) : '';

    const onValueChange = action((key: string, value: any) => {
        (state as any)[key] = value;
    });

    const handleClose = action(() => {
        state.open = false;
    });

    const handleOpen = action(() => {
        if (!!currentPatient) {
            state.currentTreatmentRegimen = currentPatient.currentTreatmentRegimen;
            state.currentTreatmentRegimenOther = currentPatient.currentTreatmentRegimenOther;
            state.depressionTreatmentStatus = currentPatient.depressionTreatmentStatus;
            state.psychDiagnosis = currentPatient.psychDiagnosis;
            state.followupSchedule = currentPatient.followupSchedule;
            state.discussionFlag = currentPatient.discussionFlag;
            state.latestScores = latestScores;
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
                currentTreatmentRegimen={currentPatient?.currentTreatmentRegimen}
                currentTreatmentRegimenOther={currentPatient?.currentTreatmentRegimenOther}
                depressionTreatmentStatus={currentPatient?.depressionTreatmentStatus}
                psychDiagnosis={currentPatient?.psychDiagnosis}
                discussionFlag={currentPatient?.discussionFlag}
                followupSchedule={currentPatient?.followupSchedule}
                onValueChange={onValueChange}
                latestScores={latestScores}
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
