import {
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    IconButton,
    List,
    ListItem,
    ListItemSecondaryAction,
    ListItemText,
} from '@material-ui/core';
import AddIcon from '@material-ui/icons/Add';
import DeleteIcon from '@material-ui/icons/Delete';
import { action } from 'mobx';
import React, { FunctionComponent } from 'react';
import { Link } from 'react-router-dom';
import { DetailPage, IDetailPageProps } from 'src/components/common/DetailPage';
import FormSection from 'src/components/Forms/FormSection';
import { getString } from 'src/services/strings';

const Examples: FunctionComponent<{ title: string; examples: string[] }> = (props) => {
    const { title, examples } = props;
    return (
        <div>
            <div>{`${title}:`}</div>
            {examples.map((ex, idx) => (
                <div key={idx}>{`${idx + 1}. ${ex}`}</div>
            ))}
        </div>
    );
};

export interface IListItem {
    id: string;
    primaryText: string;
    secondaryText: string;
}

export interface IListDetailPageProps extends IDetailPageProps {
    instruction: string;
    exampleHeaderText: string;
    examples: string[];
    listHeaderText: string;
    listHelpText: string;
    openAdd: boolean;
    addButtonText: string;
    addContent: React.ReactNode;
    canAdd: boolean;
    items: IListItem[];
    addDialogTitle: string;
    onOpenAdd: () => void;
    onCancelAdd: () => void;
    onItemDelete: (itemId: string) => void;
    onItemAdded: () => void;
    getItemLinkRoute?: (itemId: string) => string;
    onItemClick?: (itemId: string) => void;
}

export const ListDetailPage: FunctionComponent<IListDetailPageProps> = (props) => {
    const {
        title,
        onBack,
        instruction,
        exampleHeaderText,
        examples,
        listHeaderText,
        listHelpText,
        openAdd,
        canAdd,
        addButtonText,
        addContent,
        items,
        addDialogTitle,
        onOpenAdd,
        onCancelAdd,
        getItemLinkRoute,
        onItemDelete,
        onItemAdded,
        onItemClick,
    } = props;

    const handleSubmitAdd = action(() => {
        onItemAdded && onItemAdded();
    });

    return (
        <DetailPage title={title} onBack={onBack}>
            {items.length == 0 ? (
                <FormSection
                    prompt={instruction}
                    help={<Examples title={exampleHeaderText} examples={examples} />}
                    content={''}
                />
            ) : (
                <FormSection
                    prompt={listHeaderText}
                    help={listHelpText}
                    content={
                        <List>
                            {items.map((item, idx) =>
                                !!onItemClick ? (
                                    <ListItem
                                        key={idx}
                                        alignItems="flex-start"
                                        button
                                        onClick={() => onItemClick(item.id)}>
                                        <ListItemText
                                            primary={item.primaryText}
                                            secondary={item.secondaryText}
                                            primaryTypographyProps={{ noWrap: true }}
                                        />

                                        <ListItemSecondaryAction>
                                            <IconButton
                                                edge="end"
                                                aria-label="more"
                                                onClick={() => onItemDelete(item.id)}>
                                                <DeleteIcon />
                                            </IconButton>
                                        </ListItemSecondaryAction>
                                    </ListItem>
                                ) : (
                                    <ListItem
                                        key={idx}
                                        alignItems="flex-start"
                                        button
                                        component={Link}
                                        to={getItemLinkRoute ? getItemLinkRoute(item.id) : ''}>
                                        <ListItemText
                                            primary={item.primaryText}
                                            secondary={item.secondaryText}
                                            primaryTypographyProps={{ noWrap: true }}
                                        />

                                        <ListItemSecondaryAction>
                                            <IconButton
                                                edge="end"
                                                aria-label="more"
                                                onClick={() => onItemDelete(item.id)}>
                                                <DeleteIcon />
                                            </IconButton>
                                        </ListItemSecondaryAction>
                                    </ListItem>
                                )
                            )}
                        </List>
                    }
                />
            )}
            <Button variant="contained" color="primary" size="small" startIcon={<AddIcon />} onClick={onOpenAdd}>
                {addButtonText}
            </Button>
            <Dialog open={openAdd} onClose={onCancelAdd} fullWidth maxWidth="xs">
                <DialogTitle id="form-dialog-title">{addDialogTitle}</DialogTitle>
                <DialogContent>{addContent}</DialogContent>
                <DialogActions>
                    <Button onClick={onCancelAdd} color="primary">
                        {getString('Form_button_cancel')}
                    </Button>
                    <Button onClick={handleSubmitAdd} color="primary" disabled={!canAdd}>
                        {getString('Form_button_save')}
                    </Button>
                </DialogActions>
            </Dialog>
        </DetailPage>
    );
};

export default ListDetailPage;
