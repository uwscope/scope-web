import React, { FunctionComponent } from "react";

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
import { compareAsc, format } from "date-fns";
import throttle from "lodash.throttle";
import { action, observable } from "mobx";
import { observer, useLocalObservable } from "mobx-react";
import { IReviewMark } from "shared/types";
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
      reviewMark: IReviewMark;
    }>(() => ({
      reviewMark: {
        editedDateTime: new Date(),
        effectiveDateTime: new Date(),
        providerId: authStore.currentUserIdentity?.providerId,
      } as IReviewMark,
    }));

    const onRecentEntryMarkReviewed = action(() => {
      // Add a new mark effective at the current time
      const { reviewMark } = markReviewState;
      currentPatient.addReviewMark({
        ...reviewMark,
        editedDateTime: new Date(),
        effectiveDateTime: new Date(),
      });
    });

    const onRecentEntryMarkUndo = action(() => {
      // Undo reverts to the most recent effective time
      // which is less recent than the current effective time.
      // If there is no such effective time, it becomes undefined.

      // Obtain the current mark, if any
      const currentMark =
        currentPatient.reviewMarksSortedByEditedDateAndTimeDescending.length > 0
          ? currentPatient.reviewMarksSortedByEditedDateAndTimeDescending[0]
          : undefined;

      // Determine the current effectiveDateTime, if any
      const currentEffectiveDateTime = !!currentMark
        ? // It is possible that effectiveDateTime is undefined.
          currentMark.effectiveDateTime
        : undefined;

      // Obtain the most recent mark relative to that time, if any
      const mostRecentReviewMark = !!currentEffectiveDateTime
        ? currentPatient.reviewMarksSortedByEditedDateAndTimeDescending.find(
            (current) => {
              if (!current.effectiveDateTime) {
                return false;
              }

              return (
                compareAsc(
                  currentEffectiveDateTime,
                  current.effectiveDateTime,
                ) > 0
              );
            },
          )
        : undefined;

      const { reviewMark } = markReviewState;
      currentPatient.addReviewMark({
        ...reviewMark,
        editedDateTime: new Date(),
        effectiveDateTime: !!mostRecentReviewMark
          ? mostRecentReviewMark.effectiveDateTime
          : undefined,
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

    return (
      <div>
        <TitleContainer>
          <Stack direction={"row"} justifyContent={"space-between"}>
            <Stack direction={"column"} alignItems={"start"}>
              <Typography>CONTENTS</Typography>
              {!!recentEntryCutoffDateTime && (
                <FormHelperText>
                  Last Marked Reviewed:
                  <br />
                  {format(recentEntryCutoffDateTime, "MM/dd/yyyy h:mm aaa")}
                </FormHelperText>
              )}
              <Button
                variant="text"
                size="small"
                color="primary"
                sx={{ marginLeft: "-5px" }}
                disabled={((): boolean => {
                  // Undo is possible if:
                  // (1) there is no existing mark
                  // (2) there is a current mark, with an effectiveDateTime

                  // No existing mark
                  if (
                    currentPatient
                      .reviewMarksSortedByEditedDateAndTimeDescending.length ===
                    0
                  ) {
                    return false;
                  }

                  // A current mark, with an effectiveDateTime
                  if (
                    !!currentPatient
                      .reviewMarksSortedByEditedDateAndTimeDescending[0]
                      .effectiveDateTime
                  ) {
                    return false;
                  }

                  return true;
                })()}
                onClick={onRecentEntryMarkUndo}
              >
                {getString("recent_patient_entry_undo_previous_mark")}
              </Button>
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
            </Stack>
          </Stack>
        </TitleContainer>
        <List dense={true}>{contents.map(createListItem)}</List>
      </div>
    );
  },
);

export default ContentsMenu;
