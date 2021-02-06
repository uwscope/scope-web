import { List } from '@material-ui/core';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import HomeIcon from '@material-ui/icons/Home';
import TableChartIcon from '@material-ui/icons/TableChart';
import { observer } from 'mobx-react';
import { default as React, FunctionComponent } from 'react';
import { Link as RouterLink } from 'react-router-dom';

export const DrawerContent: FunctionComponent = observer(() => {
    return (
        <List>
            <ListItem button key="Home" component={RouterLink} to="/">
                <ListItemIcon>
                    <HomeIcon />
                </ListItemIcon>
                <ListItemText primary="Home" />
            </ListItem>
            <ListItem button key="Caseload" component={RouterLink} to="/caseload">
                <ListItemIcon>
                    <TableChartIcon />
                </ListItemIcon>
                <ListItemText primary="Caseload" />
            </ListItem>
        </List>
    );
});

export default DrawerContent;
