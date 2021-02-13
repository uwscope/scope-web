import { Button, Card, CardActions, CardContent, Divider, Typography, withTheme } from '@material-ui/core';
import { observer } from 'mobx-react';
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
}

export const ActionPanel: FunctionComponent<IActionPanelProps> = observer((props) => {
    const { id, actionButtons, title, children } = props;
    return (
        <Card id={id}>
            <CardTitle>
                <Typography variant="button" noWrap={true}>
                    {title}
                </Typography>
                <CardActions>
                    {!!actionButtons
                        ? actionButtons.map((a) => (
                              <Button variant="outlined" size="small" color="primary" startIcon={a.icon}>
                                  {a.text}
                              </Button>
                          ))
                        : null}
                </CardActions>
            </CardTitle>
            <Divider variant="middle" />
            <CardContent>{children}</CardContent>
        </Card>
    );
});

export default ActionPanel;
