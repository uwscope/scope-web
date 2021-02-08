import { Typography, withTheme } from '@material-ui/core';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';
import { ContentsMenu, IContentItem } from './common/ContentsMenu';

const DetailPageContainer = withTheme(
    styled.div({
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'stretch',
    })
);

const ContentContainer = withTheme(
    styled.div({
        flex: 1,
    })
);

const MenuContainer = withTheme(
    styled.div({
        position: 'sticky',
        height: '100%',
        display: 'block',
        top: 0,
    })
);

export const PatientDetailPage: FunctionComponent = observer(() => {
    const contents = [
        {
            hash: 'patient',
            label: 'Patient',
            top: true,
        },
        {
            hash: 'basic-info',
            label: 'Basic information',
        },
        {
            hash: 'treatment-info',
            label: 'Treatment information',
        },
        {
            hash: 'sessions',
            label: 'Sessions',
        },
        {
            hash: 'progress',
            label: 'Progress',
            top: true,
        },
    ] as IContentItem[];

    React.useLayoutEffect(() => {
        const handleScroll = () => {
            console.log('scroll');
        };

        window.addEventListener('scroll', handleScroll);

        return () => window.removeEventListener('scroll', handleScroll);
    });

    return (
        <DetailPageContainer>
            <ContentContainer>
                {contents.map((c) => (
                    <div style={{ height: '600px' }} id={c.hash} key={c.hash}>
                        <Typography variant={c.top ? 'h5' : 'h6'}>{c.label}</Typography>
                    </div>
                ))}
            </ContentContainer>
            <MenuContainer>
                <ContentsMenu contents={contents} />
            </MenuContainer>
        </DetailPageContainer>
    );
});

export default PatientDetailPage;
