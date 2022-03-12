import React, { createContext, FC, ReactElement, ReactNode, useContext } from 'react';
import { IRootStore } from './RootStore';

export const StoreContext = createContext<IRootStore | undefined>(undefined);

export type StoreComponent = FC<{
    store: IRootStore;
    children: ReactNode;
}>;

export const StoreProvider: StoreComponent = ({ children, store }): ReactElement => {
    // Store provider should never be accessed unless the app is ready to load patient data
    if (store?.loadState != 'Fulfilled' && store?.loadState != 'Pending') {
        store?.load();
    }

    return <StoreContext.Provider value={store}>{children}</StoreContext.Provider>;
};

export const useStores = () => useContext(StoreContext) as IRootStore;
