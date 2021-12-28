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

const store = new RootStore();

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
