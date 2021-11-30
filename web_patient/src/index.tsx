import { CssBaseline } from '@material-ui/core';
import { ThemeProvider } from '@material-ui/core/styles';
import { action, configure } from 'mobx';
import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter } from 'react-router-dom';
import App from 'src/App';
import { RootStore } from 'src/stores/RootStore';
import { StoreProvider } from 'src/stores/stores';
import createAppTheme from 'src/styles/theme';

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
                <ThemeProvider theme={theme}>
                    <BrowserRouter>
                        <App />
                    </BrowserRouter>
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

// Register service worker
if ('serviceWorker' in navigator) {
    // Use the window load event to keep the page load performant
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js');
    });
}

const randomNotification = (registration: ServiceWorkerRegistration) => {
    registration.showNotification('Showing notification from pwa');
};

// Request notification permission

console.log('Getting Permission');
Notification.requestPermission().then((result) => {
    console.log('Got permission response', result);
    if (result === 'granted') {
        navigator.serviceWorker.ready.then((registration) => {
            randomNotification(registration);
        });
    }
});
