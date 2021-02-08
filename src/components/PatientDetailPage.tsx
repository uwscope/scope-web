import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { useParams } from 'react-router';

export const PatientDetailPage: FunctionComponent = observer(() => {
    const { mrn } = useParams<{ mrn: string }>();

    return <div>{`Patient Detail here: ${mrn}`}</div>;
});

export default PatientDetailPage;
