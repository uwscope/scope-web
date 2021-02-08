import { FormControl, MenuItem, Select, withTheme } from '@material-ui/core';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';
import { ClinicCode } from '../services/types';
import { AllClinicCode } from '../stores/PatientsStore';
import { useStores } from '../stores/stores';
import { getTodayString } from '../utils/formatter';
import CaseloadTable from './CaseloadTable';
import { PageHeaderContainer, PageHeaderSubtitle, PageHeaderTitle } from './common/PageHeader';

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
    styled(Select)(() => ({
        fontSize: 34,
        '> .MuiSelect-select': {
            paddingTop: 0,
        },
    }))
);

export const CaseloadPage: FunctionComponent = observer(() => {
    const rootStore = useStores();

    const onCareManagerSelect = (event: React.ChangeEvent<{ name?: string; value: string }>) => {
        const careManager = event.target.value;
        if (!!careManager) {
            rootStore.patientsStore.selectCareManager(careManager);
        }
    };

    const onClinicSelect = (event: React.ChangeEvent<{ name?: string; value: ClinicCode | AllClinicCode }>) => {
        const clinic = event.target.value;
        if (!!clinic) {
            rootStore.patientsStore.selectClinic(clinic);
        }
    };

    const clinicFilters = [...rootStore.patientsStore.clinics, 'All Clinics'];

    return (
        <div>
            <PageHeaderContainer>
                <TitleSelectContainer>
                    <PageHeaderTitle>Caseload for</PageHeaderTitle>
                    <SelectForm>
                        <SelectInput
                            value={rootStore.patientsStore.selectedCareManager}
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
                            value={rootStore.patientsStore.selectedClinic}
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
                </TitleSelectContainer>
                <PageHeaderSubtitle>{`${getTodayString()}`}</PageHeaderSubtitle>
            </PageHeaderContainer>
            <CaseloadTable patients={rootStore.patientsStore.selectedPatients} />
        </div>
    );
});

export default CaseloadPage;
