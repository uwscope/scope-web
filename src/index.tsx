import { configure } from "mobx";
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import { RootStore } from "./stores/RootStore";
import { StoreProvider } from "./stores/stores";


// Strict enforcements for mobx
configure({
    enforceActions: "always",
    computedRequiresReaction: true,
    reactionRequiresObservable: true,
    observableRequiresReaction: true,
    disableErrorBoundaries: true
})

const store = new RootStore();

ReactDOM.render(
    <React.StrictMode>
        <StoreProvider store={store}>
            <App />
        </StoreProvider>
    </React.StrictMode>,
    document.getElementById('root')
);

// Enable hot reloading
declare let module: any;

if (module.hot) {
    module.hot.accept();
}
