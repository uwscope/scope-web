import React, { Fragment, FunctionComponent, useState } from "react";

import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import {
  Avatar,
  Button,
  FormControl,
  FormHelperText,
  InputAdornment,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { observer } from "mobx-react";
import { AuthState } from "shared/authStoreBase";
import Logo from "src/assets/scope-logo.png";
import { IAuthStore } from "src/stores/AuthStore";
import styled, { withTheme } from "styled-components";

const Container = withTheme(
  styled.div((props) => ({
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(255, 255, 255, 0.9)",
    borderRadius: props.theme.spacing(4),
    width: 400,
    padding: 50,
    [props.theme.breakpoints.down("md")]: {},
  })),
);

const LoginForm: FunctionComponent<{
  account: string;
  setAccount: (account: string) => void;
  showPassword: boolean;
  setShowPassword: (showPassword: boolean) => void;
  onShowResetPassword: () => void;
  onLogin: (username: string, password: string) => void;
  error?: string;
}> = (props) => {
  const {
    account,
    setAccount,
    showPassword,
    setShowPassword,
    onShowResetPassword,
    onLogin,
    error,
  } = props;
  const [password, setPassword] = useState("");

  const onSubmit = () => {
    // Trim the password in case it has a trailing space
    onLogin(account, password.trim());
  };

  const togglePassword = () => {
    setShowPassword(!showPassword);
  };

  const canLogin = !!account && !!password;

  return (
    <Fragment>
      <Avatar
        alt="Scope logo"
        src={Logo}
        sx={{ width: 64, height: 64 }}
        variant="square"
      />
      <h2>Welcome!</h2>
      <FormControl error={!!error} fullWidth>
        <TextField
          label="Account"
          placeholder="Enter account"
          fullWidth
          required
          margin="normal"
          variant="standard"
          value={account}
          onChange={(e) =>
            setAccount(
              // Account cannot include whitespace.
              e.target.value.replace(/\s/g, ""),
            )
          }
          InputLabelProps={{
            shrink: true,
          }}
          onKeyPress={(e) => {
            if (e.key === "Enter" && canLogin) {
              onSubmit();
            }
          }}
        />
        <TextField
          label="Password"
          placeholder="Enter password"
          type={showPassword ? "text" : "password"}
          fullWidth
          required
          variant="standard"
          margin="normal"
          value={password}
          onChange={(e) =>
            setPassword(
              // Password can include an interior space,
              // but cannot include any other whitespace.
              // We must allow a right-side space for now,
              // as additional typing could turn it into an interior space.
              // We will then trim the string whenever extracting it from this field.
              e.target.value.replace(/[\t\r\n\f]/g, "").trimStart(),
            )
          }
          InputLabelProps={{
            shrink: true,
          }}
          onKeyPress={(e) => {
            if (e.key === "Enter" && canLogin) {
              onSubmit();
            }
          }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                {showPassword ? (
                  <VisibilityIcon
                    sx={{ cursor: "pointer" }}
                    onClick={togglePassword}
                  />
                ) : (
                  <VisibilityOffIcon
                    sx={{ cursor: "pointer" }}
                    onClick={togglePassword}
                  />
                )}
              </InputAdornment>
            ),
          }}
        />
        <Stack direction="row" justifyContent="end" alignItems="center">
          <Button
            type="button"
            color="primary"
            variant="text"
            size="small"
            onClick={onShowResetPassword}
          >
            Forgot Password?
          </Button>
        </Stack>
        {error && (
          <FormHelperText error={true} sx={{ lineHeight: 1 }}>
            {error == "User does not exist."
              ? "Account incorrect."
              : error == "Incorrect username or password."
                ? "Password incorrect."
                : error == "Password attempts exceeded"
                  ? "Password attempt limit exceeded. Try again later."
                  : error}
          </FormHelperText>
        )}
        <Stack
          sx={{ paddingTop: 4 }}
          direction="row"
          justifyContent="end"
          alignItems="center"
        >
          <Button
            type="submit"
            color="primary"
            variant="contained"
            onClick={onSubmit}
            disabled={!canLogin}
          >
            Sign In
          </Button>
        </Stack>
      </FormControl>
    </Fragment>
  );
};

const PasswordResetForm: FunctionComponent<{
  account: string;
  setAccount: (account: string) => void;
  onCancelResetPassword: () => void;
  onSendResetCode: (username: string) => void;
  error?: string;
}> = (props) => {
  const { account, setAccount, onCancelResetPassword, onSendResetCode, error } =
    props;

  const onSubmit = () => {
    onSendResetCode(account);
  };

  const canSubmit = !!account;

  return (
    <Fragment>
      <Avatar
        alt="Scope logo"
        src={Logo}
        sx={{ width: 64, height: 64 }}
        variant="square"
      />
      <h2>Forgot Password?</h2>
      <Stack
        direction="column"
        spacing={2}
        justifyContent="flex-start"
        alignItems="flex-start"
      >
        <Typography variant="subtitle2">
          To reset your password, enter your SCOPE account below. We will send a
          password reset code to the email address associated with that account.
        </Typography>
        <Typography variant="subtitle2">
          If you cannot receive this code, or need other help signing in,
          contact us at &lt;
          <a href="mailto:scopestudy@uw.edu" target="_blank">
            scopestudy@uw.edu
          </a>
          &gt;.
        </Typography>
      </Stack>
      <FormControl error={!!error} fullWidth>
        <TextField
          label="Account"
          placeholder="Enter account"
          fullWidth
          required
          margin="normal"
          variant="standard"
          value={account}
          onChange={(e) =>
            setAccount(
              // Account cannot include whitespace.
              e.target.value.replace(/\s/g, ""),
            )
          }
          InputLabelProps={{
            shrink: true,
          }}
          onKeyPress={(e) => {
            if (e.key === "Enter" && canSubmit) {
              onSubmit();
            }
          }}
        />
        {error && (
          <FormHelperText error={true} sx={{ lineHeight: 1 }}>
            {error == "Username/client id combination not found."
              ? "Account incorrect."
              : error == "Attempt limit exceeded, please try after some time."
                ? "Reset attempt limit exceeded. Try again later."
                : error == "User password cannot be reset in the current state."
                  ? "Reset code not available. Contact study team."
                  : error}
          </FormHelperText>
        )}
        <Stack
          sx={{ paddingTop: 4 }}
          direction="row"
          spacing={2}
          justifyContent="space-between"
          alignItems="center"
        >
          <Button
            type="button"
            color="primary"
            variant="text"
            onClick={onCancelResetPassword}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            color="primary"
            variant="contained"
            onClick={onSubmit}
            disabled={!canSubmit}
          >
            Send Code
          </Button>
        </Stack>
      </FormControl>
    </Fragment>
  );
};

const PasswordUpdateForm: FunctionComponent<{
  showPassword: boolean;
  setShowPassword: (showPassword: boolean) => void;
  onCancelPasswordChange: () => void;
  onReset?: (resetCode: string, password: string) => void;
  onUpdate?: (password: string) => void;
  error?: string;
}> = (props) => {
  const {
    showPassword,
    setShowPassword,
    onCancelPasswordChange,
    onReset,
    onUpdate,
    error,
  } = props;
  const [resetCode, setResetCode] = useState("");
  const [password, setPassword] = useState("");
  const [passwordRepeat, setPasswordRepeat] = useState("");
  const [resetCodeHasFocus, setResetCodeHasFocus] = useState(false);
  const [resetCodeGotFocus, setResetCodeGotFocus] = useState(false);
  const [passwordGotFocus, setPasswordGotFocus] = useState(false);
  const [confirmPasswordGotFocus, setConfirmPasswordGotFocus] = useState(false);

  const isReset = !!onReset;
  const isUpdate = !!onUpdate;

  const passwordCriteria: { description: string; valid: boolean }[] = [
    {
      // Allowable length
      description: "At least 8 characters.",
      valid: password.length >= 8 && password.length <= 128,
    },
    {
      // Require uppercase
      description: "Must contain an uppercase letter.",
      valid: !!password.match(/(?=.*[A-Z])/),
    },
    {
      // Require lowercase
      description: "Must contain a lowercase letter.",
      valid: !!password.match(/(?=.*[a-z])/),
    },
    {
      // Require digit
      description: "Must contain a digit.",
      valid: !!password.match(/(?=.*[0-9])/),
    },
    {
      // Require symbol
      // Defined by Cognito as ^ $ * . [ ] { } ( ) ? " ! @ # % & / \ , > < ' : ; | _ ~ ` = + -
      // https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-policies.html
      description: "Must contain a symbol character.",
      valid: !!password.match(
        /(?=.*[\^$*.\[\]{}\(\)?“!@#%&/\\,><\’:;|_~`=+\-])/,
      ),
    },
    {
      // No space (e.g., no interior space)
      // Cognito will allow an interior space, but we will not
      description: "Must not include a space.",
      valid: !!password.match(/^\S*$/),
    },
  ];

  const validPassword =
    // Password exists
    !!password &&
    // Meets all criteria
    passwordCriteria.reduce((combinedValid, current) => {
      return combinedValid && current.valid;
    }, true);

  const canSubmit: boolean =
    // Update does not require a code
    (isUpdate ||
      // Reset requires a code
      (isReset && !!resetCode)) &&
    // Password must be valid
    validPassword &&
    // Passwords must match
    // Trim any trailing space before comparing
    // Should not matter because of trim on change
    password.trim() === passwordRepeat.trim();

  const onSubmit = () => {
    if (isUpdate) {
      canSubmit && !!onUpdate && onUpdate(password.trim());
    } else if (isReset) {
      canSubmit && !!onReset && onReset(resetCode.trim(), password.trim());
    }
  };

  const togglePassword = () => {
    setShowPassword(!showPassword);
  };

  return (
    <Fragment>
      <Avatar alt="Scope logo" src={Logo} />
      {isReset && <h2>Reset Password</h2>}
      {isUpdate && <h2>Update Password</h2>}
      <Stack
        direction="column"
        spacing={2}
        justifyContent="flex-start"
        alignItems="flex-start"
      >
        {isReset && (
          <React.Fragment>
            <Typography variant="subtitle2">
              We have sent a password reset code to the email address associated
              with your SCOPE account. The reset code will expire after 1 hour.
            </Typography>
            <Typography variant="subtitle2">
              If you cannot receive this code, or need other help signing in,
              contact us at &lt;
              <a href="mailto:scopestudy@uw.edu" target="_blank">
                scopestudy@uw.edu
              </a>
              &gt;.
            </Typography>
          </React.Fragment>
        )}
        {isUpdate && (
          <Typography variant="subtitle2">
            Sign in requires updating your SCOPE password.
          </Typography>
        )}
        <Typography variant="subtitle2">
          Create a password that meets the following criteria:
        </Typography>
        <ul style={{ alignSelf: "flex-start", marginTop: 2 }}>
          {passwordCriteria.map((current, index) => (
            <Fragment key={index}>
              <li style={{ marginLeft: "-15px" }}>
                <Typography
                  variant="subtitle2"
                  component="span"
                  sx={{
                    color:
                      passwordGotFocus && !!password.trim() && !current.valid
                        ? "error.main"
                        : undefined,
                    marginBottom: 1,
                  }}
                >
                  {current.description}
                </Typography>
              </li>
            </Fragment>
          ))}
        </ul>
      </Stack>
      <FormControl error={!!error} fullWidth>
        {isReset && (
          <TextField
            label="Reset Code"
            placeholder="Enter reset code"
            type="text"
            fullWidth
            required
            variant="standard"
            margin="normal"
            value={resetCode}
            onFocus={() => {
              setResetCodeHasFocus(true);
              setResetCodeGotFocus(true);
            }}
            onBlur={() => {
              setResetCodeHasFocus(false);
            }}
            onChange={(e) =>
              setResetCode(
                // Not allowing spaces
                e.target.value.trim(),
              )
            }
            InputLabelProps={{
              shrink: true,
            }}
            error={!resetCodeHasFocus && resetCodeGotFocus && !resetCode.trim()}
          />
        )}
        <TextField
          label="Password"
          placeholder="Enter password"
          type={showPassword ? "text" : "password"}
          fullWidth
          required
          variant="standard"
          margin="normal"
          value={password}
          onFocus={() => {
            setPasswordGotFocus(true);
          }}
          onChange={(e) =>
            setPassword(
              // Cognito allows passwords to include an interior space,
              // but that is confusing and causes issues with temporarily allowing trailing spaces.
              // We will decide to not allow creation of passwords including an interior space.
              // Continuously trim input so spaces are not added,
              // then we will separately validate lack of spaces to handle the copy-paste scenario.
              e.target.value.trim(),
            )
          }
          InputLabelProps={{
            shrink: true,
          }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                {showPassword ? (
                  <VisibilityIcon
                    sx={{ cursor: "pointer" }}
                    onClick={togglePassword}
                  />
                ) : (
                  <VisibilityOffIcon
                    sx={{ cursor: "pointer" }}
                    onClick={togglePassword}
                  />
                )}
              </InputAdornment>
            ),
          }}
          error={passwordGotFocus && !!password.trim() && !validPassword}
        />
        <TextField
          label="Confirm Password"
          placeholder="Confirm password"
          type={showPassword ? "text" : "password"}
          fullWidth
          required
          variant="standard"
          margin="normal"
          value={passwordRepeat}
          onFocus={() => {
            setConfirmPasswordGotFocus(true);
          }}
          onChange={(e) =>
            setPasswordRepeat(
              // Cognito allows passwords to include an interior space,
              // but that is confusing and causes issues with temporarily allowing trailing spaces.
              // We will decide to not allow creation of passwords including an interior space.
              // Continuously trim input so spaces are not added,
              // then we will separately validate lack of spaces to handle the copy-paste scenario.
              e.target.value.trim(),
            )
          }
          InputLabelProps={{
            shrink: true,
          }}
          onKeyPress={(e) => {
            if (e.key === "Enter" && canSubmit) {
              onSubmit();
            }
          }}
          error={
            confirmPasswordGotFocus &&
            !!passwordRepeat.trim() &&
            (!validPassword || password.trim() != passwordRepeat.trim())
          }
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                {showPassword ? (
                  <VisibilityIcon
                    sx={{ cursor: "pointer" }}
                    onClick={togglePassword}
                  />
                ) : (
                  <VisibilityOffIcon
                    sx={{ cursor: "pointer" }}
                    onClick={togglePassword}
                  />
                )}
              </InputAdornment>
            ),
          }}
        />
        {error && (
          <FormHelperText error={true} sx={{ lineHeight: 1 }}>
            {error == "Invalid verification code provided, please try again."
              ? "Password reset code incorrect."
              : error}
          </FormHelperText>
        )}
        <Stack
          sx={{ paddingTop: 4 }}
          direction="row"
          spacing={2}
          justifyContent="space-between"
          alignItems="center"
        >
          <Button
            type="button"
            color="primary"
            variant="text"
            onClick={onCancelPasswordChange}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            color="primary"
            variant="contained"
            onClick={onSubmit}
            disabled={!canSubmit}
          >
            {isReset && "Reset"}
            {isUpdate && "Update"}
          </Button>
        </Stack>
      </FormControl>
    </Fragment>
  );
};

export const Login: FunctionComponent<{ authStore: IAuthStore }> = observer(
  (props) => {
    const { authStore } = props;

    const [account, setAccount] = useState("");
    const [showPassword, setShowPassword] = useState(false);

    const onLogin = (username: string, password: string) => {
      authStore.login(username, password);
    };

    const onUpdate = (password: string) => {
      authStore.updateTempPassword(password);
    };

    const onSendResetCode = (username: string) => {
      authStore.sendResetPasswordCode(username);
    };

    const onReset = (code: string, password: string) => {
      authStore.resetPassword(code, password);
    };

    return (
      <Container>
        {authStore.authState == AuthState.UpdatePasswordInProgress ||
        authStore.authState == AuthState.ResetPasswordInProgress ? (
          <PasswordUpdateForm
            showPassword={showPassword}
            setShowPassword={setShowPassword}
            onCancelPasswordChange={() => {
              authStore.authState = AuthState.Initialized;
              authStore.clearDetail();
            }}
            onReset={
              authStore.authState == AuthState.ResetPasswordInProgress
                ? onReset
                : undefined
            }
            onUpdate={
              authStore.authState == AuthState.UpdatePasswordInProgress
                ? onUpdate
                : undefined
            }
            error={authStore.authStateDetail}
          />
        ) : authStore.authState == AuthState.ResetPasswordPrompt ? (
          <PasswordResetForm
            account={account}
            setAccount={setAccount}
            onCancelResetPassword={() => {
              authStore.authState = AuthState.Initialized;
              authStore.clearDetail();
            }}
            onSendResetCode={onSendResetCode}
            error={authStore.authStateDetail}
          />
        ) : (
          <LoginForm
            account={account}
            setAccount={setAccount}
            showPassword={showPassword}
            setShowPassword={setShowPassword}
            onShowResetPassword={() => {
              authStore.authState = AuthState.ResetPasswordPrompt;
              authStore.clearDetail();
            }}
            onLogin={onLogin}
            error={authStore.authStateDetail}
          />
        )}
      </Container>
    );
  },
);

export default Login;
