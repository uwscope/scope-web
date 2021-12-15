import {
    Avatar,
    Button,
    Checkbox,
    Container,
    FormControlLabel,
    Grid,
    Paper,
    styled,
    TextField,
} from '@material-ui/core';
import LockOutlinedIcon from '@material-ui/icons/LockOutlined';
import { observer } from 'mobx-react';
import React, { Fragment, FunctionComponent, useState } from 'react';
import { AuthState } from 'src/stores/AuthStore';
import { useStores } from 'src/stores/stores';

const PaddedPaper = styled(Paper)({
    padding: 20,
});

const LoginForm: FunctionComponent<{ onLogin: (username: string, password: string) => void }> = (props) => {
    const { onLogin } = props;
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const onSubmit = () => {
        onLogin && onLogin(email, password);
    };

    return (
        <Fragment>
            <Grid alignItems="center">
                <Avatar>
                    <LockOutlinedIcon />
                </Avatar>
                <h2>Sign In</h2>
            </Grid>
            <TextField
                label="Username"
                placeholder="Enter username"
                fullWidth
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
            />
            <TextField
                label="Password"
                placeholder="Enter password"
                type="password"
                fullWidth
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />
            <FormControlLabel control={<Checkbox name="checkedB" color="primary" />} label="Remember me" />
            <Button type="submit" color="primary" variant="contained" fullWidth onClick={onSubmit}>
                Sign in
            </Button>
        </Fragment>
    );
};

const PasswordUpdateForm: FunctionComponent<{ onUpdate: (password: string) => void }> = (props) => {
    const { onUpdate } = props;
    const [password, setPassword] = useState('');

    const onSubmit = () => {
        onUpdate && onUpdate(password);
    };

    return (
        <Fragment>
            <Grid alignItems="center">
                <Avatar>
                    <LockOutlinedIcon />
                </Avatar>
                <h2>Update password</h2>
            </Grid>
            <TextField
                label="Password"
                placeholder="Enter password"
                type="password"
                fullWidth
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />
            <FormControlLabel control={<Checkbox name="checkedB" color="primary" />} label="Remember me" />
            <Button type="submit" color="primary" variant="contained" fullWidth onClick={onSubmit}>
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
        <Container maxWidth="sm">
            <PaddedPaper elevation={10}>
                {authStore.authState == AuthState.NewPasswordRequired ? (
                    <PasswordUpdateForm onUpdate={onUpdate} />
                ) : (
                    <LoginForm onLogin={onLogin} />
                )}
            </PaddedPaper>
        </Container>
    );
});

export default Login;
