import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import { List, ListItem, ListItemIcon, ListItemText, ListSubheader } from '@mui/material';
import { action } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { useNavigate } from 'react-router';
import { Link } from 'react-router-dom';
import { DetailPage } from 'src/components/common/DetailPage';
import { getResourceLink } from 'src/services/routes';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';

export const WorksheetsHome: FunctionComponent = observer(() => {
    const rootStore = useStores();
    const { patientresources } = rootStore.appContentConfig;
    const navigate = useNavigate();

    const handleGoBack = action(() => {
        navigate(-1);
    });

    return (
        <DetailPage title={getString('Resources_title')} onBack={handleGoBack}>
            {patientresources.map((r, idx) => (
                <List
                    key={idx}
                    component="nav"
                    aria-labelledby="nested-list-subheader"
                    subheader={
                        <ListSubheader component="div" id="nested-list-subheader">
                            {r.name}
                        </ListSubheader>
                    }>
                    {r.resources.map((resource, idx) => (
                        <ListItem
                            key={idx}
                            button
                            component={Link}
                            to={getResourceLink(resource.filename)}
                            target="_blank">
                            <ListItemIcon>
                                <InsertDriveFileIcon />
                            </ListItemIcon>
                            <ListItemText primary={resource.name} />
                        </ListItem>
                    ))}
                </List>
            ))}
        </DetailPage>
    );
});

export default WorksheetsHome;
