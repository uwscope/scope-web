import {
    Button,
    Card,
    CardActions,
    CardContent,
    Divider,
    LinearProgress,
    Typography,
    withTheme,
} from '@material-ui/core';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';

const CardTitle = withTheme(
    styled.div((props) => ({
        display: 'flex',
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: props.theme.spacing(1, 1, 1, 2),
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
    children?: React.ReactNode;
    id: string;
    loading?: boolean;
}

export const ActionPanel: FunctionComponent<IActionPanelProps> = (props) => {
    const { id, actionButtons, title, children, loading = false } = props;
    return (
        <Card id={id}>
            <CardTitle>
                <Typography variant="button" noWrap={true}>
                    {title}
                </Typography>
                <CardActions>
                    {!!actionButtons
                        ? actionButtons.map((a) => (
                              <Button
                                  variant="outlined"
                                  size="small"
                                  color="primary"
                                  startIcon={a.icon}
                                  disabled={loading}
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
