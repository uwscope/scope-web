import { Button, Fade, LinearProgress, Snackbar, Stack } from '@mui/material';
import { Box } from '@mui/system';
import React, { FunctionComponent } from 'react';
import { IPromiseQueryState } from 'shared/promiseQuery';

export const ContentLoader: FunctionComponent<{
    state: IPromiseQueryState;
    name: string;
    onRetry?: () => void;
    children: React.ReactNode;
}> = (props) => {
    const { state, name, children, onRetry } = props;

    const retryAction = onRetry && (
        <Button color="secondary" size="small" onClick={onRetry}>
            RETRY
        </Button>
    );

    return (
        <Stack spacing={0}>
            <Box sx={{ height: 4 }}>
                <Fade
                    in={state.pending}
                    style={{
                        transitionDelay: state.pending ? '800ms' : '0ms',
                    }}
                    unmountOnExit
                >
                    <LinearProgress />
                </Fade>
            </Box>
            <Box sx={{ opacity: state.pending ? 0.5 : 1 }}>{children}</Box>
            <Snackbar
                open={state.error}
                message={`Sorry, there was an error retrieving ${name}. Please try again.`}
                action={retryAction}
            />
        </Stack>
    );
};

export default ContentLoader;
