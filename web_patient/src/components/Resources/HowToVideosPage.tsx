import React, { FunctionComponent } from "react";

import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { Accordion, AccordionDetails, AccordionSummary } from "@mui/material";
import withTheme from "@mui/styles/withTheme";
import { action } from "mobx";
import { useNavigate } from "react-router";
import { DetailPage } from "src/components/common/DetailPage";
import { getString } from "src/services/strings";
import styled from "styled-components";

interface IVideo {
  videoTitle: string;
  videoUrl: string;
}

interface IVideoGroup {
  screenTitle: string;
  screenVideos: IVideo[];
}

interface IIntroductoryVideos {
  groups: IVideoGroup[];
}

const getIntroductoryVideosPageState = () =>
  ({
    groups: [
      {
        screenTitle: "Introduction",
        screenVideos: [
          {
            videoTitle: "The SCOPE App",
            videoUrl: "https://player.vimeo.com/video/914972830?h=33273f2aec",
          },
        ],
      },
      {
        screenTitle: "Home Screen",
        screenVideos: [
          {
            videoTitle: "Introduction",
            videoUrl: "https://player.vimeo.com/video/915380014?h=4a48066509",
          },
          {
            videoTitle: "Your Plan for the Day",
            videoUrl: "https://player.vimeo.com/video/915381092?h=d7086e3c14",
          },
        ],
      },
      {
        screenTitle: "Tools Tab",
        screenVideos: [
          {
            videoTitle: "Introduction",
            videoUrl: "https://player.vimeo.com/video/915383443?h=566180773e",
          },
          {
            videoTitle: "Your Values & Activities Inventory",
            videoUrl: "https://player.vimeo.com/video/915383866?h=1dcb2b203e",
          },
        ],
      },
      {
        screenTitle: "Activities Tab",
        screenVideos: [
          {
            videoTitle: "Introduction",
            videoUrl: "https://player.vimeo.com/video/916144650?h=62540f2b85",
          },
          {
            videoTitle: "Updating Your Activities",
            videoUrl: "https://player.vimeo.com/video/916145231?h=cd5411fc7a",
          },
        ],
      },
      {
        screenTitle: "Progress Tab",
        screenVideos: [
          {
            videoTitle: "Introduction",
            videoUrl: "https://player.vimeo.com/video/916145616?h=0d5efd9c97",
          },
          {
            videoTitle: "Tracking Your Progress",
            videoUrl: "https://player.vimeo.com/video/916146002?h=fdd65f0f53",
          },
        ],
      },
    ],
  }) as IIntroductoryVideos;

export const HeaderText = withTheme(
  styled.div((props) => ({
    fontSize: props.theme.typography.h5.fontSize,
    fontWeight: props.theme.typography.fontWeightBold,
    lineHeight: 1.1,
    paddingBottom: "1rem",
    paddingTop: "1rem",
  })),
);

const IFrameDiv = styled.div({
  padding: "56.25% 0 0 0",
  position: "relative",
});

const IFrame = styled.iframe({
  position: "absolute",
  top: 0,
  left: 0,
  width: "100%",
  height: "100%",
  border: 0,
});

const iframeAllow: string = "fullscreen";

const playerOptions: string =
  "&" +
  [
    "byline=false",
    "dnt=true",
    "pip=false",
    "playsinline=false",
    "title=false",
  ].join("&");

export const HowToVideosPage: FunctionComponent = () => {
  const navigate = useNavigate();

  // Initially, no video is expanded.
  const [expanded, setExpanded] = React.useState<string | false>("none");

  const data = getIntroductoryVideosPageState();

  const handleChange =
    (panel: string) => (_event: React.SyntheticEvent, newExpanded: boolean) => {
      setExpanded(newExpanded ? panel : false);
    };

  const handleGoBack = action(() => {
    navigate(-1);
  });

  return (
    <DetailPage
      title={getString("Resources_howtovideos_title")}
      onBack={handleGoBack}
    >
      {data.groups.map((screen, screenIdx) => (
        <React.Fragment key={screenIdx}>
          <HeaderText>{screen.screenTitle}</HeaderText>
          {screen.screenVideos.map((video, videoIdx) => (
            <Accordion
              key={videoIdx}
              disableGutters
              expanded={expanded === `panel-${screenIdx}-${videoIdx}`}
              onChange={handleChange(`panel-${screenIdx}-${videoIdx}`)}
            >
              <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                aria-controls={`panel-${screenIdx}-${videoIdx}-content`}
                id={`panel-${screenIdx}-${videoIdx}-header`}
              >
                {video.videoTitle}
              </AccordionSummary>
              <AccordionDetails sx={{ padding: 0 }}>
                <IFrameDiv>
                  <IFrame
                    allow={iframeAllow}
                    src={video.videoUrl + playerOptions}
                    title={video.videoTitle}
                  ></IFrame>
                </IFrameDiv>
              </AccordionDetails>
            </Accordion>
          ))}
        </React.Fragment>
      ))}
      {/* This is needed for the video player */}
      <script src="https://player.vimeo.com/api/player.js"></script>
    </DetailPage>
  );
};

export default HowToVideosPage;
