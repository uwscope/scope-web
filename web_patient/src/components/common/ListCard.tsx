import { Avatar, ListItemAvatar, ListItemText, Typography } from '@mui/material';
import React, { Fragment, FunctionComponent } from 'react';

export interface IListCardProps {
    title: string;
    subtitle?: string;
    imageSrc: string;
}

export const ListCard: FunctionComponent<IListCardProps> = (props) => {
    const { title, subtitle, imageSrc } = props;

    return (
        <Fragment>
            <ListItemAvatar>
                <Avatar alt={title} src={imageSrc} variant="square" />
            </ListItemAvatar>
            <ListItemText
                primary={title}
                secondary={
                    <Typography sx={{ display: 'inline' }} variant="body2">
                        {subtitle}
                    </Typography>
                }
            />
        </Fragment>
    );
};

export default ListCard;
