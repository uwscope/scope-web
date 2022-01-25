import {
    Avatar,
    Button,
    Checkbox,
    FormControlLabel,
    TextField,
} from '@mui/material';
import { observer } from 'mobx-react';
import React, { Fragment, FunctionComponent, useState } from 'react';
import Logo from 'src/assets/scope-logo.png';
import { AuthState } from 'src/stores/AuthStore';
import { useStores } from 'src/stores/stores';
import styled, { withTheme } from 'styled-components';

const Container = withTheme(
    styled.div((props) => ({
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        borderRadius: props.theme.spacing(4),
        width: 400,
        padding: 50,
        [props.theme.breakpoints.down('md')]: {},
    }))
);

const ButtonContainer = styled.div({
    alignSelf: 'flex-end',
    paddingTop: 20,
});

const LoginForm: FunctionComponent<{
    onLogin: (username: string, password: string) => void;
}> = (props) => {
    const { onLogin } = props;
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const onSubmit = () => {
        onLogin && onLogin(email, password);
    };

    return (
        <Fragment>
            <Avatar alt="Scope logo" src={Logo} />
            <h2>Welcome!</h2>
            <TextField
                label="Username"
                placeholder="Enter username"
                fullWidth
                required
                variant="standard"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                InputLabelProps={{
                    shrink: true,
                }}
            />
            <TextField
                label="Password"
                placeholder="Enter password"
                type="password"
                fullWidth
                required
                variant="standard"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                InputLabelProps={{
                    shrink: true,
                }}
            />
            <ButtonContainer>
                <FormControlLabel
                    control={<Checkbox name="checkedB" color="primary" />}
                    label="Remember me"
                />
                <Button
                    type="submit"
                    color="primary"
                    variant="contained"
                    onClick={onSubmit}
                >
                    Sign in
                </Button>
            </ButtonContainer>
        </Fragment>
    );
};

const PasswordUpdateForm: FunctionComponent<{
    onUpdate: (password: string) => void;
}> = (props) => {
    const { onUpdate } = props;
    const [password, setPassword] = useState('');

    const onSubmit = () => {
        onUpdate && onUpdate(password);
    };

    return (
        <Fragment>
            <Avatar alt="Scope logo" src={Logo} />
            <h2>Update password</h2>
            <TextField
                label="Password"
                placeholder="Enter password"
                type="password"
                fullWidth
                required
                variant="standard"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                InputLabelProps={{
                    shrink: true,
                }}
            />
            <FormControlLabel
                control={<Checkbox name="checkedB" color="primary" />}
                label="Remember me"
            />
            <Button
                type="submit"
                color="primary"
                variant="contained"
                fullWidth
                onClick={onSubmit}
            >
                Update password
            </Button>
        </Fragment>
    );
};

export const Login: FunctionComponent = observer(() => {
    const { authStore } = useStores();

    const onLogin = (username: string, password: string) => {
        authStore.login(username, password);
    };

    const onUpdate = (password: string) => {
        authStore.updateTempPassword(password);
    };

    return (
        <Container>
            {authStore.authState == AuthState.NewPasswordRequired ? (
                <PasswordUpdateForm onUpdate={onUpdate} />
            ) : (
                <LoginForm onLogin={onLogin} />
            )}
        </Container>
    );
});

export default Login;
