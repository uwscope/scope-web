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
    handleSave?: () => void;
    disableSave?: boolean;
}> = (props) => {
    const { open, title, content, error, loading, handleCancel, handleSave, disableSave } = props;

    return (
        <Dialog open={open} fullWidth>
            <DialogTitle id="form-dialog-title">{title}</DialogTitle>
            <DialogContent dividers>
                <Stack spacing={2}>
                    <Box sx={{ opacity: loading ? 0.5 : 1, pointerEvents: loading ? 'none' : 'auto' }}>{content}</Box>
                </Stack>
            </DialogContent>
            <Box sx={{ height: 1 }}>
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
                <Stack direction="column" alignItems="flex-end">
                    {error && (
                        <Typography variant="caption" color="error" sx={{ lineHeight: 1 }}>
                            {getString('dialog_error_text')}
                        </Typography>
                    )}
                    <Stack direction="row">
                        {handleCancel && (
                            <Button onClick={handleCancel} color="primary">
                                {getString('dialog_action_cancel')}
                            </Button>
                        )}
                        {handleSave && (
                            <Button onClick={handleSave} color="primary" disabled={disableSave}>
                                {getString('dialog_action_save')}
                            </Button>
                        )}
                    </Stack>
                </Stack>
            </DialogActions>
        </Dialog>
    );
};

export default StatefulDialog;
