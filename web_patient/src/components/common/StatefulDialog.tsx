import {
    Dialog,
    DialogTitle,
    DialogContent,
    Stack,
    Typography,
    DialogActions,
    Button,
    Box,
    Fade,
    LinearProgress,
} from '@mui/material';
import React, { FunctionComponent } from 'react';
import { getString } from 'src/services/strings';

export const StatefulDialog: FunctionComponent<{
    open: boolean;
    title: string | React.ReactChild;
    content: string | React.ReactChild;
    error?: boolean;
    loading?: boolean;
    handleCancel?: () => void;
    handleYes?: () => void;
    handleNo?: () => void;
    handleDelete?: () => void;
    handleSave?: () => void;
    disableSave?: boolean;
}> = (props) => {
    const {
        open,
        title,
        content,
        error,
        loading,
        handleCancel,
        handleYes,
        handleNo,
        handleDelete,
        handleSave,
        disableSave,
    } = props;
    return (
        <Dialog open={open} fullWidth maxWidth="phone">
            <DialogTitle id="form-dialog-title">{title}</DialogTitle>
            <DialogContent>
                <Stack spacing={2}>
                    <Box sx={{ opacity: loading ? 0.5 : 1, pointerEvents: loading ? 'none' : 'auto' }}>{content}</Box>
                    {error && (
                        <Typography variant="caption" color="error" sx={{ lineHeight: 1 }}>
                            {getString('Form_error_text')}
                        </Typography>
                    )}
                </Stack>
            </DialogContent>
            <Box sx={{ height: 4 }}>
                <Fade
                    in={loading}
                    style={{
                        transitionDelay: loading ? '800ms' : '0ms',
                    }}
                    unmountOnExit>
                    <LinearProgress />
                </Fade>
            </Box>
            <DialogActions sx={{ opacity: loading ? 0.5 : 1, pointerEvents: loading ? 'none' : 'auto' }}>
                {handleYes && (
                    <Button onClick={handleYes} color="primary">
                        {getString('Form_button_yes')}
                    </Button>
                )}
                {handleNo && (
                    <Button onClick={handleNo} color="primary">
                        {getString('Form_button_no')}
                    </Button>
                )}
                {handleCancel && (
                    <Button onClick={handleCancel} color="primary">
                        {getString('Form_button_cancel')}
                    </Button>
                )}
                {handleDelete && (
                    <Button onClick={handleDelete} color="primary">
                        {getString('Form_button_delete')}
                    </Button>
                )}
                {handleSave && (
                    <Button onClick={handleSave} color="primary" disabled={disableSave}>
                        {getString('Form_button_save')}
                    </Button>
                )}
            </DialogActions>
        </Dialog>
    );
};

export default StatefulDialog;
