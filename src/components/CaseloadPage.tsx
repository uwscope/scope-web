import { FormControl, MenuItem, Select, withTheme } from '@material-ui/core';
import Typography from '@material-ui/core/Typography';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';
import { useStores } from '../stores/stores';
import { getTodayString } from '../utils/formatter';
import { PageHeaderContainer, PageHeaderSubtitle, PageHeaderTitle } from './common/PageHeader';

const TitleSelectContainer = withTheme(
    styled.div({
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'baseline',
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

    const onClinicSelect = (event: React.ChangeEvent<{ name?: string; value: string }>) => {
        const clinic = event.target.value;
        if (!!clinic) {
            rootStore.patientsStore.selectClinic(clinic);
        }
    };

    return (
        <div>
            <PageHeaderContainer>
                <TitleSelectContainer>
                    <PageHeaderTitle variant="h4">Caseload for</PageHeaderTitle>
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
                    <PageHeaderTitle variant="h4">in</PageHeaderTitle>
                    <SelectForm>
                        <SelectInput
                            value={rootStore.patientsStore.selectedClinic}
                            onChange={onClinicSelect}
                            inputProps={{
                                name: 'clinic',
                                id: 'clinic',
                            }}>
                            {rootStore.patientsStore.clinics.map((c) => (
                                <MenuItem key={c} value={c}>
                                    {c}
                                </MenuItem>
                            ))}
                        </SelectInput>
                    </SelectForm>
                </TitleSelectContainer>
                <PageHeaderSubtitle>{`${getTodayString()}`}</PageHeaderSubtitle>
            </PageHeaderContainer>
            <Typography paragraph>
                This is caseload. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
                incididunt ut labore et dolore magna aliqua. Rhoncus dolor purus non enim praesent elementum facilisis
                leo vel. Risus at ultrices mi tempus imperdiet. Semper risus in hendrerit gravida rutrum quisque non
                tellus. Convallis convallis tellus id interdum velit laoreet id donec ultrices. Odio morbi quis commodo
                odio aenean sed adipiscing. Amet nisl suscipit adipiscing bibendum est ultricies integer quis. Cursus
                euismod quis viverra nibh cras. Metus vulputate eu scelerisque felis imperdiet proin fermentum leo.
                Mauris commodo quis imperdiet massa tincidunt. Cras tincidunt lobortis feugiat vivamus at augue. At
                augue eget arcu dictum varius duis at consectetur lorem. Velit sed ullamcorper morbi tincidunt. Lorem
                donec massa sapien faucibus et molestie ac.
            </Typography>
        </div>
    );
});

export default CaseloadPage;
