import { observer } from "mobx-react";
import React, { FunctionComponent } from "react";
import { useStores } from "./stores/stores";


export const App: FunctionComponent = observer(() => {
    const rootStore = useStores();
    return (
        <div className="App">
            <p>{rootStore.userStore.name}</p>
            {rootStore.authStore.loggedIn ?
                <button onClick={() => rootStore.logout()}>Logout</button> :
                <button onClick={() => rootStore.login()}>Login</button>}
        </div>
    );
});

export default App;
