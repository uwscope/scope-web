import { Button, FormControl, MenuItem, Select, withTheme } from '@material-ui/core';
import AddIcon from '@material-ui/icons/Add';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { useHistory } from 'react-router-dom';
import CaseloadTable from 'src/components/caseload/CaseloadTable';
import { Page, PageHeaderContainer, PageHeaderSubtitle, PageHeaderTitle } from 'src/components/common/Page';
import { AddPatientProfileDialog } from 'src/components/PatientDetail/PatientProfileDialog';
import { AllClinicCode, ClinicCode } from 'src/services/enums';
import { IPatientProfile } from 'src/services/types';
import { useStores } from 'src/stores/stores';
import { getTodayString } from 'src/utils/formatter';
import styled from 'styled-components';

const TitleSelectContainer = withTheme(
    styled.div({
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'baseline',
        flexWrap: 'wrap',
    })
);

const SelectForm = withTheme(
    styled(FormControl)((props) => ({
        margin: props.theme.spacing(0, 2),
        minWidth: 240,
    }))
);

const SelectInput = withTheme(
    styled(Select)((props) => ({
        ...props.theme.typography.h5,
        '> .MuiSelect-select': {
            paddingTop: 0,
        },
    }))
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

    const clinicFilters = [...rootStore.patientsStore.clinics, 'All Clinics'];

    const onPatientClick = (recordId: string) => {
        history.push(`/patient/${recordId}`);
    };

    const handleClose = action(() => {
        state.open = false;
    });

    const handleOpen = action(() => {
        state.open = true;
    });

    const onSave = action((newPatient: IPatientProfile) => {
        rootStore.patientsStore.addPatient(newPatient);
        state.open = false;
    });

    React.useEffect(() => {
        rootStore.patientsStore.getPatients();
    }, []);

    return (
        <Page>
            <PageHeaderContainer loading={rootStore.patientsStore.state == 'Pending'}>
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
                            {rootStore.patientsStore.careManagers.map((cm) => (
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
                            {clinicFilters.map((c) => (
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
                <PageHeaderSubtitle>{`${getTodayString()}`}</PageHeaderSubtitle>
            </PageHeaderContainer>
            <CaseloadTable patients={rootStore.patientsStore.filteredPatients} onPatientClick={onPatientClick} />
            <AddPatientProfileDialog open={state.open} onClose={handleClose} onAddPatient={onSave} />
        </Page>
    );
});

export default CaseloadPage;
