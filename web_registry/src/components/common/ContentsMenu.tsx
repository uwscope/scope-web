import React, { FunctionComponent } from "react";

import AssignmentReturnOutlinedIcon from "@mui/icons-material/AssignmentReturnOutlined";
import AssignmentTurnedInOutlinedIcon from "@mui/icons-material/AssignmentTurnedInOutlined";
import {
  Badge,
  Button,
  FormHelperText,
  List,
  ListItem,
  ListItemProps,
  ListItemText,
  Stack,
  Typography,
  useTheme,
} from "@mui/material";
import withTheme from "@mui/styles/withTheme";
import { format } from "date-fns";
import throttle from "lodash.throttle";
import { action, observable } from "mobx";
import { observer, useLocalObservable } from "mobx-react";
import { IRecentEntryReview } from "shared/types";
import { getString } from "src/services/strings";
import { usePatient, useStores } from "src/stores/stores";
import styled, { CSSObject, ThemedStyledProps } from "styled-components";

const TitleContainer = withTheme(
  styled.div((props) => ({
    padding: props.theme.spacing(2.5, 2.5, 1, 2.5),
  })),
);

const ContentListBadge = withTheme(
  styled(Badge)(
    () =>
      ({
        // This seems to work well enough, but I do not understand it.
        "& .MuiBadge-badge": {
          right: "-20px",
          top: "50%",
        },
      }) as CSSObject,
  ),
);

const ContentListItem = withTheme(
  styled(ListItem)(
    (
      props: ThemedStyledProps<
        ListItemProps & { $active: boolean; $top: boolean },
        any
      >,
    ) => ({
      borderLeft: "4px solid",
      borderLeftColor: props.$active
        ? props.theme.palette.primary.light
        : "white",
      paddingLeft: props.$top ? props.theme.spacing(2) : props.theme.spacing(4),
      ">.MuiListItemText-root": {
        textTransform: props.$top ? "uppercase" : null,
      } as CSSObject,
    }),
  ),
);

export interface IContentItem {
  hash: string;
  label: string;
  recentEntryBadgeContent?: React.ReactNode;
  top?: boolean;
}

export interface IContentsMenuProps {
  contents: IContentItem[];
  contentId: string;
  recentEntryCutoffDateTime: Date | undefined;
  recentEntryBadgeContent: React.ReactNode;
}

const noop = () => {};

const useThrottledOnScroll = (
  callback: any,
  delay: number,
  contentId: string,
) => {
  const throttledCallback = React.useMemo(
    () => (callback ? throttle(callback, delay) : noop),
    [callback, delay],
  ) as any;

  React.useEffect(() => {
    if (throttledCallback === noop) {
      return undefined;
    }

    const mainBody = document.querySelector(contentId);
    if (!!mainBody) {
      mainBody.addEventListener("scroll", throttledCallback);
    }

    return () => {
      if (!!mainBody) {
        mainBody.removeEventListener("scroll", throttledCallback);
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

export const ContentsMenu: FunctionComponent<IContentsMenuProps> = observer(
  (props) => {
    const {
      contents,
      contentId,
      recentEntryCutoffDateTime,
      recentEntryBadgeContent,
    } = props;
    const currentPatient = usePatient();
    const { authStore } = useStores();
    const theme = useTheme();

    const markReviewState = useLocalObservable<{
      recentEntryReview: IRecentEntryReview;
    }>(() => ({
      recentEntryReview: {
        editedDateTime: new Date(),
        effectiveDateTime: new Date(),
        providerId: authStore.currentUserIdentity?.providerId,
      } as IRecentEntryReview,
    }));

    const onRecentEntryMarkReviewed = action(() => {
      const { recentEntryReview } = markReviewState;
      currentPatient.addRecentEntryReview({
        ...recentEntryReview,
        editedDateTime: new Date(),
        effectiveDateTime: new Date(),
      });
    });

    const onRecentEntryMarkUndo = action(() => {
      const previousRecentEntryReview =
        currentPatient.recentEntryReviewsSortedByDateAndTimeDescending[1];
      const { recentEntryReview } = markReviewState;
      currentPatient.addRecentEntryReview({
        ...recentEntryReview,
        editedDateTime: new Date(),
        effectiveDateTime: previousRecentEntryReview.effectiveDateTime,
      });
    });

    const itemsClientRef = React.useRef<ContentMenuItem[]>([]);
    React.useEffect(() => {
      itemsClientRef.current = contents.map((c) => {
        return {
          ...c,
          node: document.getElementById(c.hash),
        };
      });

      action(() => (state.activeHash = undefined))();
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

      const mainBody = document.querySelector(contentId) as HTMLElement;

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
            mainBody.scrollTop +
              document.documentElement.clientHeight / 8 +
              theme.customSizes.headerHeight
        ) {
          active = item;
          break;
        }
      }

      setActiveHash(active ? active.hash : undefined);
    }, [state.activeHash, contents]);

    // Corresponds to 10 frames at 60 Hz
    useThrottledOnScroll(
      contents.length > 0 ? action(findActiveIndex) : null,
      166,
      contentId,
    );

    const handleClick = (hash: string) => {
      // Used to disable findActiveIndex if the page scrolls due to a click
      clickedRef.current = true;
      unsetClickedRef.current = setTimeout(() => {
        clickedRef.current = false;
      }, 1000);

      if (state.activeHash !== hash) {
        setActiveHash(hash);

        const mainBody = document.querySelector(contentId);
        if (!!mainBody) {
          const element = document.getElementById(hash);

          if (!!element) {
            mainBody.scrollBy({
              top:
                element.getBoundingClientRect().top -
                theme.customSizes.headerHeight -
                24,
              behavior: "smooth",
            });
          }
        }
      }
    };

    React.useEffect(
      () => () => {
        clearTimeout(unsetClickedRef.current as NodeJS.Timeout);
      },
      [],
    );

    const createListItem = (content: IContentItem) => {
      return (
        <ContentListItem
          button
          key={content.hash}
          $active={state.activeHash == content.hash}
          $top={content.top}
          onClick={action(() => handleClick(content.hash))}
        >
          <ListItemText disableTypography={true}>
            <ContentListBadge
              badgeContent={content.recentEntryBadgeContent}
              color={"primary"}
            >
              <Typography variant="body2">{content.label}</Typography>
            </ContentListBadge>
          </ListItemText>
        </ContentListItem>
      );
    };

    // return (
    //   <div>
    //     <TitleContainer>
    //       <Stack direction={"column"}>
    //         <Typography>CONTENTS</Typography>
    //         {!!recentEntryCutoffDateTime && !!recentEntryBadgeContent && (
    //           <FormHelperText>
    //             New Since:
    //             <br />
    //             {format(recentEntryCutoffDateTime, "MM/dd/yyyy h:mm aaa")}
    //           </FormHelperText>
    //         )}
    //       </Stack>
    //     </TitleContainer>
    //     <List dense={true}>{contents.map(createListItem)}</List>
    //   </div>
    // );

    return (
      <div>
        <TitleContainer>
          <Stack direction={"row"} justifyContent={"space-between"}>
            <Stack direction={"column"} alignItems={"start"}>
              <Typography>CONTENTS</Typography>
              <FormHelperText>
                Last Reviewed:
                <br />
                {format(recentEntryCutoffDateTime, "MM/dd/yyyy h:mm aaa")}
              </FormHelperText>
            </Stack>
            <Stack direction={"column"} alignItems={"start"} spacing={1}>
              <Button
                variant="outlined"
                size="small"
                color="primary"
                disabled={!recentEntryBadgeContent}
                startIcon={<AssignmentTurnedInOutlinedIcon />}
                onClick={onRecentEntryMarkReviewed}
              >
                {getString("recent_patient_entry_mark_reviewed")}
              </Button>
              <Button
                variant="text"
                size="small"
                color="primary"
                disabled={
                  currentPatient.recentEntryReviewsSortedByDateAndTimeDescending
                    .length <= 1
                }
                startIcon={<AssignmentReturnOutlinedIcon />}
                onClick={onRecentEntryMarkUndo}
              >
                {getString("recent_patient_entry_undo_previous_mark")}
              </Button>
            </Stack>
          </Stack>
        </TitleContainer>
        <List dense={true}>{contents.map(createListItem)}</List>
      </div>
    );
  },
);

export default ContentsMenu;
