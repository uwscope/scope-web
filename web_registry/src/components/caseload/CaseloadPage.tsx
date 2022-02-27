import AddIcon from '@mui/icons-material/Add';
import { Button, FormControl, MenuItem, Select } from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { useHistory } from 'react-router-dom';
import { AllClinicCode, ClinicCode } from 'shared/enums';
import { IPatientProfile } from 'shared/types';
import CaseloadTable from 'src/components/caseload/CaseloadTable';
import PageLoader from 'src/components/chrome/PageLoader';
import { Page, PageHeaderContainer, PageHeaderTitle } from 'src/components/common/Page';
import { AddPatientProfileDialog } from 'src/components/PatientDetail/PatientProfileDialog';
import { useStores } from 'src/stores/stores';
import styled from 'styled-components';

const TitleSelectContainer = withTheme(
    styled.div({
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        flexWrap: 'wrap',
        height: 48,
    }),
);

const SelectForm = withTheme(
    styled(FormControl)((props) => ({
        margin: props.theme.spacing(0, 2),
        minWidth: 240,
    })),
);

const SelectInput = withTheme(
    styled(Select)((props) => ({
        ...props.theme.typography.h5,
        '>.MuiSelect-select': {
            minHeight: 'auto',
        },
    })),
);

const ActionButtonContainer = styled.div({
    flexGrow: 1,
    display: 'flex',
    justifyContent: 'flex-end',
});

const state = observable<{ open: boolean }>({
    open: false,
});

export const CaseloadPage: FunctionComponent = observer(() => {
    const rootStore = useStores();
    const history = useHistory();

    const onCareManagerSelect = action((event: React.ChangeEvent<{ name?: string; value: string }>) => {
        const careManager = event.target.value;
        if (!!careManager) {
            rootStore.patientsStore.filterCareManager(careManager);
        }
    });

    const onClinicSelect = action((event: React.ChangeEvent<{ name?: string; value: ClinicCode | AllClinicCode }>) => {
        const clinic = event.target.value;
        if (!!clinic) {
            rootStore.patientsStore.filterClinic(clinic);
        }
    });

    const onPatientClick = (recordId: string) => {
        history.push(`/patient/${recordId}`);
    };

    const handleClose = action(() => {
        state.open = false;
    });

    const handleOpen = action(() => {
        state.open = true;
    });

    const onSave = action((newProfile: IPatientProfile) => {
        rootStore.patientsStore.addPatient({ profile: newProfile });
        state.open = false;
    });

    React.useEffect(() => {
        rootStore.patientsStore.load();
    }, []);

    return (
        <Page>
            <PageLoader
                state={rootStore.patientsStore.state}
                name="the registry"
                hasValue={rootStore.patientsStore.patients.length > 0}>
                <PageHeaderContainer>
                    <TitleSelectContainer>
                        <PageHeaderTitle>Caseload for</PageHeaderTitle>
                        <SelectForm>
                            <SelectInput
                                value={rootStore.patientsStore.filteredCareManager}
                                onChange={onCareManagerSelect}
                                inputProps={{
                                    name: 'caremanager',
                                    id: 'caremanager',
                                }}>
                                {rootStore.patientsStore.filterableCareManagers.map((cm) => (
                                    <MenuItem key={cm} value={cm}>
                                        {cm}
                                    </MenuItem>
                                ))}
                            </SelectInput>
                        </SelectForm>
                        <PageHeaderTitle>in</PageHeaderTitle>
                        <SelectForm>
                            <SelectInput
                                value={rootStore.patientsStore.filteredClinic}
                                onChange={onClinicSelect}
                                inputProps={{
                                    name: 'clinic',
                                    id: 'clinic',
                                }}>
                                {rootStore.patientsStore.filterableClinics.map((c) => (
                                    <MenuItem key={c} value={c}>
                                        {c}
                                    </MenuItem>
                                ))}
                            </SelectInput>
                        </SelectForm>
                        <ActionButtonContainer>
                            <Button
                                variant="outlined"
                                size="small"
                                color="primary"
                                startIcon={<AddIcon />}
                                key="Add patient"
                                onClick={handleOpen}>
                                Add patient
                            </Button>
                        </ActionButtonContainer>
                    </TitleSelectContainer>
                </PageHeaderContainer>
                <CaseloadTable patients={rootStore.patientsStore.filteredPatients} onPatientClick={onPatientClick} />
                <AddPatientProfileDialog
                    open={state.open}
                    onClose={handleClose}
                    onAddPatient={onSave}
                    careManagers={rootStore.patientsStore.careManagers}
                />
            </PageLoader>
        </Page>
    );
});

export default CaseloadPage;
