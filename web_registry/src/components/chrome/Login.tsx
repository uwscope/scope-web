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
    const [account, setAccount] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);

    const onSubmit = () => {
        // Trim the password in case it has a trailing space
        onLogin && onLogin(account, password.trim());
    };

    const togglePassword = () => {
        setShowPassword(!showPassword);
    };

    const canLogin = !!account && !!password;

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
                    value={account}
                    onChange={(e) => setAccount(
                        // Username cannot include whitespace.
                        e.target.value.replace(/\s/g, '')
                    )}
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
                    onChange={(e) => setPassword(
                        // Password can include an interior space,
                        // but cannot include any other whitespace.
                        // We must allow a right-side space for now,
                        // as additional typing could turn it into an interior space.
                        // We will then trim the string whenever extracting it from this field.
                        e.target.value.replace(/[\t\r\n\f]/g, '').trimStart()
                    )}
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

    const validPassword =
        // Password exists
        !!password &&
        // Allowable length
        (password.length >= 8) &&
        (password.length <= 128) &&
        // No space (e.g., no interior space)
        // Cognito will allow an interior space, but we will not
        !!password.match(/^\S+$/) &&
        // Require uppercase
        !!password.match(/(?=.*[A-Z])/) &&
        // Require lowercase
        !!password.match(/(?=.*[a-z])/) &&
        // Require digit
        !!password.match(/(?=.*[0-9])/) &&
        // Require symbol
        // Defined by Cognito as ^ $ * . [ ] { } ( ) ? " ! @ # % & / \ , > < ' : ; | _ ~ ` = + -
        // https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-policies.html
        !!password.match(/(?=.*[\^$*.\[\]{}\(\)?“!@#%&/\\,><\’:;|_~`=+\-])/);

    const canSubmit: boolean =
        validPassword &&
        // Passwords must match
        // Trim any trailing space before comparing
        // Should not matter because of trim on change
        (password.trim() === passwordRepeat.trim());

    const onSubmit = () => {
        canSubmit && !!onUpdate && onUpdate(password.trim());
    };

    const togglePassword = () => {
        setShowPassword(!showPassword);
    };

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
                <li>
                    <Typography variant="caption">Must not include spaces</Typography>
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
                    onChange={(e) => setPassword(
                        // Cognito allows passwords to include an interior space,
                        // but that is confusing and causes issues with temporarily allowing trailing spaces.
                        // We will decide to not allow creation of passwords including an interior space.
                        // Continuously trim input so spaces are not added,
                        // then we will separately validate lack of spaces to handle the copy-paste scenario.
                        e.target.value.trim()
                    )}
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
                    error={!validPassword}
                />
                <TextField
                    label="Confirm Password"
                    placeholder="Confirm password"
                    type="password"
                    fullWidth
                    required
                    variant="standard"
                    margin="normal"
                    value={passwordRepeat}
                    onChange={(e) => setPasswordRepeat(
                        // Cognito allows passwords to include an interior space,
                        // but that is confusing and causes issues with temporarily allowing trailing spaces.
                        // We will decide to not allow creation of passwords including an interior space.
                        // Continuously trim input so spaces are not added,
                        // then we will separately validate lack of spaces to handle the copy-paste scenario.
                        e.target.value.trim()
                    )}
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
