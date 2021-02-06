import { CssBaseline } from '@material-ui/core';
import { ThemeProvider } from '@material-ui/core/styles';
import { configure } from 'mobx';
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import { RootStore } from './stores/RootStore';
import { StoreProvider } from './stores/stores';
import createAppTheme from './styles/theme';

// Strict enforcements for mobx
configure({
    enforceActions: 'always',
    computedRequiresReaction: true,
    reactionRequiresObservable: true,
    observableRequiresReaction: true,
    disableErrorBoundaries: true,
});

const store = new RootStore();

const theme = createAppTheme();

ReactDOM.render(
    <React.StrictMode>
        <CssBaseline>
            <StoreProvider store={store}>
                <ThemeProvider theme={theme}>
                    <App />
                </ThemeProvider>
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
