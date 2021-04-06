import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Grid } from '@material-ui/core';
import EditIcon from '@material-ui/icons/Edit';
import { differenceInYears } from 'date-fns';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { GridDateField, GridDropdownField, GridTextField } from 'src/components/common/GridField';
import { clinicCodeValues, patientSexValues } from 'src/services/enums';
import { IMedicalInfo } from 'src/services/types';
import { useStores } from 'src/stores/stores';

interface IMedicalInfoContentProps extends Partial<IMedicalInfo> {
    editable?: boolean;
    onValueChange: (key: string, value: any) => void;
}

const MedicalInfoContent: FunctionComponent<IMedicalInfoContentProps> = (props) => {
    const { editable, primaryCareManager, sex, birthdate, clinicCode, onValueChange } = props;

    return (
        <Grid container spacing={2} alignItems="stretch">
            <GridTextField
                editable={editable}
                label="Care Manager"
                value={primaryCareManager}
                onChange={(text) => onValueChange('primaryCareManager', text)}
            />
            <GridDropdownField
                editable={editable}
                label="Sex"
                value={sex}
                options={patientSexValues}
                onChange={(text) => onValueChange('sex', text)}
            />
            <GridDateField
                editable={editable}
                label="Date of Birth"
                value={birthdate}
                onChange={(text) => onValueChange('birthdate', text)}
            />
            <GridTextField
                editable={false}
                label="Age"
                value={differenceInYears(new Date(), birthdate ?? new Date())}
            />
            <GridDropdownField
                editable={editable}
                label="Clinic code"
                value={clinicCode}
                options={clinicCodeValues}
                onChange={(text) => onValueChange('clinicCode', text)}
            />
        </Grid>
    );
};

const state = observable<{ open: boolean } & IMedicalInfo>({
    open: false,
    primaryCareManager: '',
    sex: 'Male',
    birthdate: new Date(),
    clinicCode: 'Breast',
});

export const MedicalInfo: FunctionComponent = observer(() => {
    const { currentPatient } = useStores();

    const onValueChange = action((key: string, value: any) => {
        (state as any)[key] = value;
    });

    const handleClose = action(() => {
        state.open = false;
    });

    const handleOpen = action(() => {
        if (!!currentPatient) {
            state.primaryCareManager = currentPatient.primaryCareManager;
            state.sex = currentPatient.sex;
            state.birthdate = currentPatient.birthdate;
            state.clinicCode = currentPatient.clinicCode;
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
            id="medical"
            title="Medical Information"
            loading={currentPatient?.state == 'Pending'}
            actionButtons={[{ icon: <EditIcon />, text: 'Edit', onClick: handleOpen } as IActionButton]}>
            <MedicalInfoContent
                editable={false}
                primaryCareManager={currentPatient?.primaryCareManager}
                sex={currentPatient?.sex}
                birthdate={currentPatient?.birthdate}
                clinicCode={currentPatient?.clinicCode}
                onValueChange={onValueChange}
            />

            <Dialog open={state.open} onClose={handleClose}>
                <DialogTitle>Edit Medical Information</DialogTitle>
                <DialogContent>
                    <MedicalInfoContent editable={true} {...state} onValueChange={onValueChange} />
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

export default MedicalInfo;
