import { Avatar, Button, FormControl, FormHelperText, InputAdornment, TextField, Typography } from '@mui/material';
import { observer } from 'mobx-react';
import React, { Fragment, FunctionComponent, useState } from 'react';
import { AuthState } from 'shared/authStoreBase';
import Logo from 'src/assets/scope-logo.png';
import { IAuthStore } from 'src/stores/AuthStore';
import styled, { withTheme } from 'styled-components';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';

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
    })),
);

const ButtonContainer = styled.div({
    alignSelf: 'flex-end',
    paddingTop: 20,
});

const LoginForm: FunctionComponent<{
    onLogin: (username: string, password: string) => void;
    error?: string;
}> = (props) => {
    const { onLogin, error } = props;
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);

    const onSubmit = () => {
        onLogin && onLogin(email, password);
    };

    const togglePassword = () => {
        setShowPassword(!showPassword);
    };

    const canLogin = !!email && !!password;

    return (
        <Fragment>
            <Avatar alt="Scope logo" src={Logo} sx={{ width: 64, height: 64 }} variant="square" />
            <h2>Welcome!</h2>
            <FormControl error={!!error} fullWidth>
                <TextField
                    label="Username"
                    placeholder="Enter username"
                    fullWidth
                    required
                    margin="normal"
                    variant="standard"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    InputLabelProps={{
                        shrink: true,
                    }}
                    onKeyPress={(e) => {
                        if (e.key === 'Enter' && canLogin) {
                            onSubmit();
                        }
                    }}
                />
                <TextField
                    label="Password"
                    placeholder="Enter password"
                    type={showPassword ? 'text' : 'password'}
                    fullWidth
                    required
                    variant="standard"
                    margin="normal"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    InputLabelProps={{
                        shrink: true,
                    }}
                    onKeyPress={(e) => {
                        if (e.key === 'Enter' && canLogin) {
                            onSubmit();
                        }
                    }}
                    InputProps={{
                        endAdornment: (
                            <InputAdornment position="end">
                                {showPassword ? (
                                    <VisibilityIcon sx={{ cursor: 'pointer' }} onClick={togglePassword} />
                                ) : (
                                    <VisibilityOffIcon sx={{ cursor: 'pointer' }} onClick={togglePassword} />
                                )}
                            </InputAdornment>
                        ),
                    }}
                />
                {error && (
                    <FormHelperText id="component-error-text" sx={{ lineHeight: 1 }}>
                        {error}
                    </FormHelperText>
                )}
                <ButtonContainer>
                    <Button type="submit" color="primary" variant="contained" onClick={onSubmit} disabled={!canLogin}>
                        Sign in
                    </Button>
                </ButtonContainer>
            </FormControl>
        </Fragment>
    );
};

const PasswordUpdateForm: FunctionComponent<{
    onUpdate: (password: string) => void;
    error?: string;
}> = (props) => {
    const { onUpdate, error } = props;
    const [password, setPassword] = useState('');
    const [passwordRepeat, setPasswordRepeat] = useState('');
    const [showPassword, setShowPassword] = useState(false);

    const onSubmit = () => {
        onUpdate && onUpdate(password);
    };

    const togglePassword = () => {
        setShowPassword(!showPassword);
    };

    const canSubmit = !!password && password === passwordRepeat;

    return (
        <Fragment>
            <Avatar alt="Scope logo" src={Logo} />
            <h2>Update password</h2>
            <Typography variant="subtitle2">Please generate a password that meets the following criteria:</Typography>
            <ul style={{ alignSelf: 'flex-start' }}>
                <li>
                    <Typography variant="caption">At least 8 characters</Typography>
                </li>
                <li>
                    <Typography variant="caption">Must contain uppercase letters</Typography>
                </li>
                <li>
                    <Typography variant="caption">Must contain lowercase letters</Typography>
                </li>
                <li>
                    <Typography variant="caption">Must contain digits</Typography>
                </li>
                <li>
                    <Typography variant="caption">Must contain symbol characters</Typography>
                </li>
            </ul>
            <FormControl error={!!error} fullWidth>
                <TextField
                    label="Password"
                    placeholder="Enter password"
                    type={showPassword ? 'text' : 'password'}
                    fullWidth
                    required
                    variant="standard"
                    margin="normal"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    InputLabelProps={{
                        shrink: true,
                    }}
                    InputProps={{
                        endAdornment: (
                            <InputAdornment position="end">
                                {showPassword ? (
                                    <VisibilityIcon sx={{ cursor: 'pointer' }} onClick={togglePassword} />
                                ) : (
                                    <VisibilityOffIcon sx={{ cursor: 'pointer' }} onClick={togglePassword} />
                                )}
                            </InputAdornment>
                        ),
                    }}
                />
                <TextField
                    label="Password-retype"
                    placeholder="Retype password"
                    type="password"
                    fullWidth
                    required
                    variant="standard"
                    margin="normal"
                    value={passwordRepeat}
                    onChange={(e) => setPasswordRepeat(e.target.value)}
                    InputLabelProps={{
                        shrink: true,
                    }}
                    onKeyPress={(e) => {
                        if (e.key === 'Enter' && canSubmit) {
                            onSubmit();
                        }
                    }}
                    error={!canSubmit}
                />
                {error && (
                    <FormHelperText id="component-error-text" sx={{ lineHeight: 1 }}>
                        {error}
                    </FormHelperText>
                )}
                <ButtonContainer>
                    <Button type="submit" color="primary" variant="contained" onClick={onSubmit} disabled={!canSubmit}>
                        Update password
                    </Button>
                </ButtonContainer>
            </FormControl>
        </Fragment>
    );
};

export const Login: FunctionComponent<{ authStore: IAuthStore }> = observer((props) => {
    const { authStore } = props;

    const onLogin = (username: string, password: string) => {
        authStore.login(username, password);
    };

    const onUpdate = (password: string) => {
        authStore.updateTempPassword(password);
    };

    return (
        <Container>
            {authStore.authState == AuthState.NewPasswordRequired ? (
                <PasswordUpdateForm onUpdate={onUpdate} error={authStore.authStateDetail} />
            ) : (
                <LoginForm onLogin={onLogin} error={authStore.authStateDetail} />
            )}
        </Container>
    );
});

export default Login;
