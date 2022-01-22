import AdapterDateFns from '@mui/lab/AdapterDateFns';
import LocalizationProvider from '@mui/lab/LocalizationProvider';
import { CssBaseline } from '@mui/material';
import { StyledEngineProvider, Theme, ThemeProvider } from '@mui/material/styles';
import { action, configure } from 'mobx';
import React from 'react';
import ReactDOM from 'react-dom';
import App from 'src/App';
import { RootStore } from 'src/stores/RootStore';
import { StoreProvider } from 'src/stores/stores';
import createAppTheme from 'src/styles/theme';
import { IAppConfig } from "shared/types";
import { combineUrl } from "src/utils/url";

declare module '@mui/styles/defaultTheme' {
    // eslint-disable-next-line @typescript-eslint/no-empty-interface
    interface DefaultTheme extends Theme {}
}

// Strict enforcements for mobx
configure({
    enforceActions: 'always',
    computedRequiresReaction: true,
    reactionRequiresObservable: true,
    // observableRequiresReaction: true,
    disableErrorBoundaries: true,
});

// Synchronously obtain a server configuration, use it to configure the RootStore.
// This synchronous call could be removed if the app had a "loading" state.
const xhr = new XMLHttpRequest();
xhr.open("GET", combineUrl(CLIENT_CONFIG.flaskBaseUrl, "app/config"),false);
xhr.send();
// As more is added to serverConfig, it will become a type.
const serverConfig: IAppConfig = JSON.parse(xhr.response) as IAppConfig;

// Create the RootStore
const store = new RootStore(serverConfig);

// TODO: Temporary login
action(() => store.load())();

const theme = createAppTheme();

ReactDOM.render(
    <React.StrictMode>
        <CssBaseline>
            <StoreProvider store={store}>
                <StyledEngineProvider injectFirst>
                    <ThemeProvider theme={theme}>
                        <LocalizationProvider dateAdapter={AdapterDateFns}>
                            <App />
                        </LocalizationProvider>
                    </ThemeProvider>
                </StyledEngineProvider>
            </StoreProvider>
        </CssBaseline>
    </React.StrictMode>,
    document.getElementById('root')
);

// Enable hot reloading
declare let module: any;

if (module.hot) {
    module.hot.accept();
}
