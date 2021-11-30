import { ListItem, ListItemIcon, ListItemText, Typography } from '@material-ui/core';
import CheckIcon from '@material-ui/icons/Check';
import RadioButtonUncheckedIcon from '@material-ui/icons/RadioButtonUnchecked';
import React, { FunctionComponent } from 'react';
import { IScheduledTaskItem } from 'src/services/types';
import { getTaskItemDueTimeString } from 'src/utils/schedule';

export interface IScheduledListItemProps {
    item: IScheduledTaskItem;
    onClick?: () => void;
}

export const ScheduledListItem: FunctionComponent<IScheduledListItemProps> = (props) => {
    const { item, onClick } = props;

    return (
        <ListItem button onClick={onClick} disabled={item.completed}>
            <ListItemIcon style={{ justifyContent: 'center' }}>
                {item.completed ? <CheckIcon /> : <RadioButtonUncheckedIcon />}
            </ListItemIcon>
            <ListItemText
                primary={<Typography noWrap>{item.name}</Typography>}
                secondary={getTaskItemDueTimeString(item, new Date())}
            />
        </ListItem>
    );
};

export default ScheduledListItem;
