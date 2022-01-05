import { Button, Card, CardActions, CardContent, Divider, Grid, LinearProgress, Typography } from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';

const CardTitle = withTheme(
    styled.div((props) => ({
        height: 42,
        padding: props.theme.spacing(2),
    }))
);

const TitleType = styled(Typography)({});

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
                <Grid container spacing={2} direction="row" justifyContent="space-between" alignItems="center">
                    <Grid item p={0}>
                        <TitleType variant="h6" noWrap={true}>
                            {title}
                        </TitleType>
                    </Grid>
                    <Grid item flexGrow={1}>
                        {inlineTitle && <InlineType>{`(${inlineTitle})`}</InlineType>}
                    </Grid>
                    <Grid item>
                        <CardActions sx={{ padding: 0, minHeight: 28 }}>
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
                    </Grid>
                </Grid>
            </CardTitle>
            {loading ? <Loading /> : <Divider variant="middle" />}
            <CardContent sx={{ padding: 3 }}>{children}</CardContent>
        </Card>
    );
};

export default ActionPanel;
