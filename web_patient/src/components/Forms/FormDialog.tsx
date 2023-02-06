import CloseIcon from '@mui/icons-material/Close';
import KeyboardArrowLeft from '@mui/icons-material/KeyboardArrowLeft';
import KeyboardArrowRight from '@mui/icons-material/KeyboardArrowRight';
import { LoadingButton } from '@mui/lab';
import {
    Alert,
    AppBar,
    Box,
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
    IconButton,
    MobileStepper,
    Slide,
    Snackbar,
    Toolbar,
    Typography,
} from '@mui/material';
import { TransitionProps } from '@mui/material/transitions';
import withTheme from '@mui/styles/withTheme';
import { action, runInAction } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { useNavigate } from 'react-router';
import { getString } from 'src/services/strings';
import styled from 'styled-components';

export interface IFormPage {
    content: React.ReactElement;
    title?: string;
    canGoNext?: boolean;
    onSubmit?: () => Promise<boolean>;
    submitToast?: string;
}

export interface IFormDialogProps {
    isOpen: boolean;
    title?: string;
    canClose?: boolean;
    loading?: boolean;
    onClose?: () => void;
    onSubmit?: () => Promise<boolean>;
    pages: IFormPage[];
    submitToast?: string;
}

const ContentContainer = styled.div({
    marginTop: 56,
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    width: '100%',
    overflow: 'hidden',
});

const PageContent = withTheme(
    styled.div((props) => ({
        flex: 1,
        overflowY: 'auto',
        overflowX: 'hidden',
        padding: props.theme.spacing(2),
        [props.theme.breakpoints.up('phone')]: {
            padding: props.theme.spacing(2),
        },
        [props.theme.breakpoints.up('tablet')]: {
            padding: props.theme.spacing(4),
        },
        [props.theme.breakpoints.up('laptop')]: {
            padding: props.theme.spacing(8),
        },
    })),
);

const Transition = React.forwardRef(
    (props: TransitionProps & { children: React.ReactElement }, ref: React.Ref<unknown>) => {
        return <Slide direction="up" ref={ref} {...props} />;
    },
);

export const FormDialog: FunctionComponent<IFormDialogProps> = observer((props) => {
    const { isOpen, pages, canClose, onClose, loading } = props;
    const navigate = useNavigate();

    const state = useLocalObservable<{
        closeConfirmOpen: boolean;
        activePage: number;
        submitErrorOpen: boolean;
        submitSuccessOpen: boolean;
    }>(() => ({
        closeConfirmOpen: false,
        activePage: 0,
        submitErrorOpen: false,
        submitSuccessOpen: false,
    }));

    const canBack: () => boolean = action(() => {
        // Cannot go back from a first page
        if (state.activePage === 0) {
            return false;
        }

        // Cannot go back to a page which already submitted
        if (!!pages[state.activePage].onSubmit) {
            return false;
        }

        // Cannot go back if currently loading
        if (!loading) {
            return false;
        }

        return true;
    });

    const forceClose = action(() => {
        state.closeConfirmOpen = false;
        onClose && onClose();

        navigate(-1);
    });

    const closeAction = action(() => {
        if (!!canClose) {
            forceClose();
        } else {
            state.closeConfirmOpen = true;
        }
    });

    const dismissConfirmClose = action(() => {
        state.closeConfirmOpen = false;
    });

    const maxPages = pages.length;
    const setActivePage = action((index: number) => {
        state.activePage = index;
    });

    const title = (() => {
        if (pages[state.activePage].title) {
            return pages[state.activePage].title;
        } else if (props.title) {
            return props.title;
        } else {
            return undefined;
        }
    })();

    const submitToast = (() => {
        if (pages[state.activePage].submitToast) {
            return pages[state.activePage].submitToast;
        } else if (props.submitToast) {
            return props.submitToast;
        } else {
            return undefined;
        }
    })();

    const handleNext = action(async () => {
        const isFinalPage = state.activePage == maxPages - 1;

        // If this page has a submit handler,
        // execute the page submit handler
        const pageSubmit = pages[state.activePage].onSubmit;

        // If this is the final page of the form,
        // execute any form submit handler
        const formSubmit = isFinalPage && props.onSubmit;

        const submitNeeded = !!pageSubmit || !!formSubmit;
        if (submitNeeded) {
            // Perform the desired submissions
            let submitSuccess = true;
            if (submitSuccess && pageSubmit) {
                submitSuccess = await pageSubmit();
            }
            if (submitSuccess && formSubmit) {
                submitSuccess = await formSubmit();
            }

            runInAction(() => {
            // In case of error, do not advance the form.
            // In case of success, the success closer handler will advance the form.
            state.submitErrorOpen = false;
                if (submitSuccess) {
                    state.submitSuccessOpen = true;
                } else {
                    state.submitErrorOpen = true;
                }
            });
        } else {
            // Without any submission, just advance the page.
            // If already on the final page, close the form.
            if (!isFinalPage) {
                const nextPage = Math.min(maxPages - 1, state.activePage + 1);
                setActivePage(nextPage);
            } else {
                forceClose();
            }
        }
    });

    const handleBack = action(() => {
        setActivePage(Math.max(0, state.activePage - 1));
    });

    const handleSubmitSuccessClose = action(() => {
        state.submitSuccessOpen = false;

        const isFinalPage = state.activePage == maxPages - 1;
        if (!isFinalPage) {
            const nextPage = Math.min(maxPages - 1, state.activePage + 1);
            setActivePage(nextPage);
        } else {
            forceClose();
        }
    });

    const handleSnackbarClose = action(() => {
        state.submitErrorOpen = false;
    });

    const isNextSubmit: () => boolean = action(() => {
        // The last page is submit
        if(state.activePage === maxPages - 1) {
            return true;
        }

        // A page with a submit handler is submit
        if(!!pages[state.activePage].onSubmit) {
            return true;
        }

        return false;
    });

    return (
        <Dialog fullScreen open={isOpen} onClose={closeAction} TransitionComponent={Transition}>
            <AppBar>
                <Toolbar>
                    <IconButton
                        edge="start"
                        color="inherit"
                        onClick={closeAction}
                        aria-label="close"
                        size="large"
                        disabled={loading}>
                        <CloseIcon />
                    </IconButton>
                    {!!title && (<Typography variant="h6">{title}</Typography>)}
                </Toolbar>
            </AppBar>
            <ContentContainer>
                <PageContent>
                    <Box sx={{ opacity: loading ? 0.5 : 1, pointerEvents: loading ? 'none' : 'auto' }}>
                        {pages[state.activePage].content}
                    </Box>
                </PageContent>
                <MobileStepper
                    sx={{ background: '#eee' }}
                    steps={maxPages}
                    position="static"
                    variant="text"
                    activeStep={state.activePage}
                    nextButton={
                        <LoadingButton
                            loading={loading}
                            onClick={handleNext}
                            disabled={!pages[state.activePage].canGoNext}>
                            {isNextSubmit()
                                ? getString('Form_button_submit')
                                : getString('Form_button_next')
                            }
                            <KeyboardArrowRight />
                        </LoadingButton>
                    }
                    backButton={
                        <Button
                            onClick={handleBack}
                            disabled={!canBack()}
                            sx={{visibility: state.activePage > 0 ? 'visible' : 'hidden'}}
                        >
                            {<KeyboardArrowLeft />}
                            {getString('Form_button_back')}
                        </Button>
                    }
                />
            </ContentContainer>
            <Dialog open={state.closeConfirmOpen}>
                <DialogContent>
                    <DialogContentText>{getString('Form_confirm_close')}</DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button color="primary" onClick={() => forceClose()}>
                        {getString('Form_button_yes')}
                    </Button>
                    <Button color="primary" autoFocus onClick={dismissConfirmClose}>
                        {getString('Form_button_no')}
                    </Button>
                </DialogActions>
            </Dialog>
            <Snackbar open={state.submitErrorOpen} autoHideDuration={6000} onClose={handleSnackbarClose}>
                <Alert
                    severity="error"
                    action={
                        <Button color="primary" size="small" onClick={handleNext}>
                            {getString('Form_submit_error_retry')}
                        </Button>
                    }>
                    {getString('Form_submit_error_message')}
                </Alert>
            </Snackbar>
            {submitToast && (
                <Dialog open={state.submitSuccessOpen} onClose={handleSubmitSuccessClose}>
                    <DialogTitle>{getString('Form_submit_thankyou')}</DialogTitle>
                    <DialogContent>
                        <Typography variant="body1" sx={{ lineHeight: '1.14rem' }}>
                            {submitToast}
                        </Typography>
                    </DialogContent>
                    <DialogActions>
                        <Button color="primary" onClick={handleSubmitSuccessClose}>
                            {getString('Form_button_ok')}
                        </Button>
                    </DialogActions>
                </Dialog>
            )}
        </Dialog>
    );
});

export default FormDialog;
