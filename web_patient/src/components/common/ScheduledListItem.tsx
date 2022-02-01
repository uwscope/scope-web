import { ListItem, ListItemIcon, ListItemText, Typography } from '@mui/material';
import CheckIcon from '@mui/icons-material/Check';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import React, { FunctionComponent } from 'react';
import { IScheduledActivity } from 'shared/types';
import { getTaskItemDueTimeString } from 'src/utils/schedule';

export interface IScheduledListItemProps {
    item: IScheduledActivity;
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
                primary={<Typography noWrap>{item.activityName}</Typography>}
                secondary={getTaskItemDueTimeString(item, new Date())}
            />
        </ListItem>
    );
};

export default ScheduledListItem;
