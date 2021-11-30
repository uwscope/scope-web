import { AppBar, Dialog, IconButton, Slide, Toolbar, Typography, withTheme } from '@material-ui/core';
import { TransitionProps } from '@material-ui/core/transitions';
import CloseIcon from '@material-ui/icons/Close';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';

export interface IProgressDialogProps {
    isOpen: boolean;
    title: string;
    onClose: () => void;
    content: React.ReactNode;
}

const ContentContainer = withTheme(
    styled.div((props) => ({
        marginTop: 56,
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        width: '100%',
        overflowX: 'hidden',
        overflowY: 'auto',
        padding: props.theme.spacing(2),
    }))
);

const Transition = React.forwardRef(function Transition(
    props: TransitionProps & { children?: React.ReactElement },
    ref: React.Ref<unknown>
) {
    return <Slide direction="up" ref={ref} {...props} />;
});

export const ProgressDialog: FunctionComponent<IProgressDialogProps> = (props) => {
    const { isOpen, title, content, onClose } = props;

    return (
        <Dialog fullScreen open={isOpen} TransitionComponent={Transition} onClose={onClose}>
            <AppBar>
                <Toolbar>
                    <IconButton edge="start" color="inherit" aria-label="close" onClick={onClose}>
                        <CloseIcon />
                    </IconButton>
                    <Typography variant="h6" noWrap>
                        {title}
                    </Typography>
                </Toolbar>
            </AppBar>
            <ContentContainer>{content}</ContentContainer>
        </Dialog>
    );
};

export default ProgressDialog;
