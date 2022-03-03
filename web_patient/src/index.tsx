import AdapterDateFns from '@mui/lab/AdapterDateFns';
import LocalizationProvider from '@mui/lab/LocalizationProvider';
import { CssBaseline } from '@mui/material';
import { StyledEngineProvider, Theme, ThemeProvider } from '@mui/material/styles';
import { configure } from 'mobx';
import React from 'react';
import ReactDOM from 'react-dom';
import App from 'src/App';
import createAppTheme from 'src/styles/theme';
import { isDev } from 'shared/env';

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
    disableErrorBoundaries: !isDev,
    useProxies: 'never',
});

const theme = createAppTheme();

ReactDOM.render(
    <React.StrictMode>
        <CssBaseline>
            <StyledEngineProvider injectFirst>
                <ThemeProvider theme={theme}>
                    <LocalizationProvider dateAdapter={AdapterDateFns}>
                        <App />
                    </LocalizationProvider>
                </ThemeProvider>
            </StyledEngineProvider>
        </CssBaseline>
    </React.StrictMode>,
    document.getElementById('root')
);

// Enable hot reloading
declare let module: any;

if (module.hot) {
    module.hot.accept();
}
