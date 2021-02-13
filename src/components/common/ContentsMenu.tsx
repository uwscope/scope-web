import {
    Card,
    CardContent,
    List,
    ListItem,
    ListItemProps,
    ListItemText,
    Typography,
    useTheme,
    withTheme,
} from '@material-ui/core';
import throttle from 'lodash.throttle';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import styled, { ThemedStyledProps } from 'styled-components';

const MenuContainer = withTheme(
    styled.div((props) => ({
        width: props.theme.customSizes.contentsMenuWidth,
        marginLeft: props.theme.spacing(3),
    }))
);

// TODO: issue prevents setting text transform https://github.com/mui-org/material-ui/issues/16307
const ContentListItem = withTheme(
    styled(ListItem)((props: ThemedStyledProps<ListItemProps & { $active: boolean; $top: boolean }, any>) => ({
        borderLeft: '4px solid',
        borderLeftColor: props.$active ? props.theme.palette.primary.light : 'white',
        paddingLeft: props.$top ? props.theme.spacing(2) : props.theme.spacing(4),
    }))
);

export interface IContentItem {
    hash: string;
    label: string;
    top?: boolean;
}

export interface IContentsMenuProps {
    contents: IContentItem[];
}

const noop = () => {};

const useThrottledOnScroll = (callback: any, delay: number) => {
    const throttledCallback = React.useMemo(() => (callback ? throttle(callback, delay) : noop), [
        callback,
        delay,
    ]) as any;

    React.useEffect(() => {
        if (throttledCallback === noop) {
            return undefined;
        }

        const mainBody = document.querySelector('main');
        if (!!mainBody) {
            mainBody.addEventListener('scroll', throttledCallback);
        }

        return () => {
            if (!!mainBody) {
                mainBody.removeEventListener('scroll', throttledCallback);
            }
            throttledCallback.cancel();
        };
    }, [throttledCallback]);
};

const state = observable<{ activeHash: string | undefined }>({
    activeHash: undefined,
});

const setActiveHash = (hash: string | undefined) => {
    state.activeHash = hash;
};

type ContentMenuItem = IContentItem & { node: HTMLElement | null };

export const ContentsMenu: FunctionComponent<IContentsMenuProps> = observer((props) => {
    const { contents } = props;
    const theme = useTheme();

    const itemsClientRef = React.useRef<ContentMenuItem[]>([]);
    React.useEffect(() => {
        itemsClientRef.current = contents.map((c) => {
            return {
                ...c,
                node: document.getElementById(c.hash),
            };
        });
    }, [contents]);

    const clickedRef = React.useRef(false);
    const unsetClickedRef = React.useRef<NodeJS.Timeout | null>(null);
    const findActiveIndex = React.useCallback(() => {
        // set default if activeHash is null
        if (state.activeHash == null) {
            setActiveHash(contents[0].hash);
        }

        // Don't set the active index based on scroll if a link was just clicked
        if (clickedRef.current) {
            return;
        }

        const mainBody = document.querySelector('main') as HTMLElement;

        let active: ContentMenuItem | undefined;
        for (let i = itemsClientRef.current.length - 1; i >= 0; i -= 1) {
            // No hash if we're near the top of the page
            if (mainBody.scrollTop < theme.customSizes.headerHeight) {
                active = undefined;
                break;
            }

            const item = itemsClientRef.current[i];

            if (
                item.node &&
                item.node.offsetTop <
                    mainBody.scrollTop + document.documentElement.clientHeight / 8 + theme.customSizes.headerHeight
            ) {
                active = item;
                break;
            }
        }

        setActiveHash(active ? active.hash : undefined);
    }, [state.activeHash, contents]);

    // Corresponds to 10 frames at 60 Hz
    useThrottledOnScroll(contents.length > 0 ? action(findActiveIndex) : null, 166);

    const handleClick = (hash: string) => {
        // Used to disable findActiveIndex if the page scrolls due to a click
        clickedRef.current = true;
        unsetClickedRef.current = setTimeout(() => {
            clickedRef.current = false;
        }, 1000);

        if (state.activeHash !== hash) {
            setActiveHash(hash);

            const mainBody = document.querySelector('main');
            if (!!mainBody) {
                const element = document.getElementById(hash);

                if (!!element) {
                    mainBody.scrollBy({
                        top: element.getBoundingClientRect().top - theme.customSizes.headerHeight - theme.spacing(3),
                        behavior: 'smooth',
                    });
                }
            }
        }
    };

    React.useEffect(
        () => () => {
            clearTimeout(unsetClickedRef.current as NodeJS.Timeout);
        },
        []
    );

    const createListItem = (content: IContentItem) => {
        return (
            <ContentListItem
                button
                key={content.hash}
                $active={state.activeHash == content.hash}
                $top={content.top}
                onClick={action(() => handleClick(content.hash))}>
                <ListItemText primary={content.label} />
            </ContentListItem>
        );
    };

    return (
        <MenuContainer>
            <Card>
                <CardContent>
                    <Typography variant="h6">Contents</Typography>
                    <List dense={true}>{contents.map(createListItem)}</List>
                </CardContent>
            </Card>
        </MenuContainer>
    );
});

export default ContentsMenu;
