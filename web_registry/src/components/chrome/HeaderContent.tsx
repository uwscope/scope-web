import { Avatar, Breadcrumbs, Grid, Link, Menu, MenuItem, withTheme } from '@material-ui/core';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { useHistory, useRouteMatch } from 'react-router';
import Logo from 'src/assets/scope-logo.png';
import PatientSearch from 'src/components/chrome/PatientSearch';
import { useStores } from 'src/stores/stores';
import styled from 'styled-components';

const Title = styled(Grid)({
    flexGrow: 1,
});

const BreadcrumbPath = withTheme(
    styled(Breadcrumbs)((props) => ({
        flexGrow: 1,
        color: props.theme.palette.primary.contrastText,
    }))
);

const state = observable<{ anchorEl: HTMLElement | null }>({
    anchorEl: null,
});

export const HeaderContent: FunctionComponent = observer(() => {
    const rootStore = useStores();
    const history = useHistory();

    let match = useRouteMatch('/patient/:recordId');

    var patientName = '';
    if (!!match && !!match.params) {
        const { recordId } = match?.params as any;
        if (!!recordId) {
            const currentPatient = rootStore.getPatientByRecordId(recordId);
            if (!!currentPatient) {
                patientName = currentPatient.name;
            }
        }
    }

    const onPatientSelect = (name: string) => {
        console.log('TODO: selected', name);
    };

    const handleClickName = action((event: React.MouseEvent<HTMLElement>) => {
        state.anchorEl = event.currentTarget;
    });

    const handleLogout = action(() => {
        rootStore.authStore.logout();
        state.anchorEl = null;
    });

    const handleClose = action(() => {
        state.anchorEl = null;
    });

    return (
        <Grid container direction="row" justify="flex-start" alignItems="center" spacing={2}>
            <Grid item>
                <Avatar alt="Scope logo" src={Logo} />
            </Grid>
            <Title item>
                <Typography variant="h6">{rootStore.appTitle}</Typography>
            </Title>
            {!!patientName ? (
                <BreadcrumbPath>
                    <Link href="#" color="inherit" onClick={() => history.goBack()}>
                        <Typography>Registry</Typography>
                    </Link>
                    <Typography>{patientName}</Typography>
                </BreadcrumbPath>
            ) : null}
            <Grid item>
                <PatientSearch
                    options={rootStore.patientsStore.patients.map((p) => p.name)}
                    onSelect={onPatientSelect}
                />
            </Grid>
            <div>
                <Menu
                    id="lock-menu"
                    anchorEl={state.anchorEl}
                    keepMounted
                    open={Boolean(state.anchorEl)}
                    onClose={() => handleClose()}>
                    <MenuItem onClick={(_) => handleLogout()}>Log out</MenuItem>
                </Menu>
                <Button color="inherit" onClick={(e) => handleClickName(e)}>
                    {rootStore.currentUserIdentity?.name}
                </Button>
            </div>
        </Grid>
    );
});

export default HeaderContent;
