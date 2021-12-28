import {
    Button,
    Card,
    CardActions,
    CardContent,
    Divider,
    LinearProgress,
    Typography,
} from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';

const CardTitle = withTheme(
    styled.div((props) => ({
        display: 'flex',
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: props.theme.spacing(1, 1, 1, 2),
        height: 64,
    }))
);

const TitleType = styled(Typography)({
    fontSize: '1rem',
    fontWeight: 600,
});

const InlineType = withTheme(
    styled.span((props) => ({
        fontSize: '0.8rem',
        fontWeight: 400,
        color: 'rgba(0, 0, 0, 0.54)',
        paddingLeft: props.theme.spacing(1),
    }))
);

const Loading = withTheme(styled(LinearProgress)({ height: 1 }));

export interface IActionButton {
    icon?: React.ReactNode;
    text: string;
    onClick: () => void;
}

export interface IActionPanelProps {
    actionButtons?: IActionButton[];
    title: string;
    inlineTitle?: string;
    children?: React.ReactNode;
    id: string;
    loading?: boolean;
}

export const ActionPanel: FunctionComponent<IActionPanelProps> = (props) => {
    const { id, actionButtons, title, inlineTitle, children, loading = false } = props;
    return (
        <Card id={id}>
            <CardTitle>
                <div>
                    <TitleType variant="button" noWrap={true}>
                        {title}
                    </TitleType>
                    {inlineTitle && <InlineType>{`(${inlineTitle})`}</InlineType>}
                </div>
                <CardActions>
                    {!!actionButtons
                        ? actionButtons.map((a) => (
                              <Button
                                  variant="outlined"
                                  size="small"
                                  color="primary"
                                  startIcon={a.icon}
                                  disabled={loading || !a.onClick}
                                  onClick={a.onClick}
                                  key={a.text}>
                                  {a.text}
                              </Button>
                          ))
                        : null}
                </CardActions>
            </CardTitle>
            {loading ? <Loading /> : <Divider variant="middle" />}
            <CardContent>{children}</CardContent>
        </Card>
    );
};

export default ActionPanel;
