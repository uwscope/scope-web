import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import Chrome from './components/Chrome';

export const App: FunctionComponent = observer(() => {
    return <Chrome></Chrome>;
});

export default App;
