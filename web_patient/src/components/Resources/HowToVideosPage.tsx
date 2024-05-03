import React, { FunctionComponent } from "react";

import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { Accordion, AccordionDetails, AccordionSummary } from "@mui/material";
import withTheme from "@mui/styles/withTheme";
import { action } from "mobx";
import { useNavigate } from "react-router";
import { DetailPage } from "src/components/common/DetailPage";
import { getString } from "src/services/strings";
import styled from "styled-components";

export interface IVideo {
  videoTitle: string;
  videoUrl: string;
}

export interface IScreen {
  screenTitle: string;
  screenVideos: IVideo[];
}

export interface IHowToVideosPageState {
  mainVideoTitle: string;
  mainVideoUrl: string;
  screens: IScreen[];
}

const getHowToVideosPageState = () =>
  ({
    mainVideoTitle: "Introduction to the SCOPE App",
    mainVideoUrl:
      "https://player.vimeo.com/video/914972830?h=33273f2aec&amp;badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479",
    screens: [
      {
        screenTitle: "Home Screen",
        screenVideos: [
          {
            videoTitle: "Introduction",
            videoUrl:
              "https://player.vimeo.com/video/915380014?h=4a48066509&amp;badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479",
          },
          {
            videoTitle: "Your Plan for the Day",
            videoUrl:
              "https://player.vimeo.com/video/915381092?h=d7086e3c14&amp;badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479",
          },
        ],
      },
      {
        screenTitle: "Tools Tab",
        screenVideos: [
          {
            videoTitle: "Introduction",
            videoUrl:
              "https://player.vimeo.com/video/915383443?h=566180773e&amp;badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479",
          },
          {
            videoTitle: "Your Values & Activities Inventory",
            videoUrl:
              "https://player.vimeo.com/video/915383866?h=1dcb2b203e&amp;badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479",
          },
        ],
      },
      {
        screenTitle: "Activities Tab",
        screenVideos: [
          {
            videoTitle: "Introduction",
            videoUrl:
              "https://player.vimeo.com/video/916144650?h=62540f2b85&amp;badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479",
          },
          {
            videoTitle: "Updating Your Activities",
            videoUrl:
              "https://player.vimeo.com/video/916145231?h=cd5411fc7a&amp;badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479",
          },
        ],
      },
      {
        screenTitle: "Progress Tab",
        screenVideos: [
          {
            videoTitle: "Introduction",
            videoUrl:
              "https://player.vimeo.com/video/916145616?h=0d5efd9c97&amp;badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479",
          },
          {
            videoTitle: "Tracking Your Progress",
            videoUrl:
              "https://player.vimeo.com/video/916146002?h=fdd65f0f53&amp;badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479",
          },
        ],
      },
    ],
  }) as IHowToVideosPageState;

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
  allow: "autoplay; fullscreen; picture-in-picture; clipboard-write",
  position: "absolute",
  top: 0,
  left: 0,
  width: "100%",
  height: "100%",
  border: 0,
});

export const HowToVideosPage: FunctionComponent = () => {
  const navigate = useNavigate();

  // Default value of expanded is "main-panel" which is the Introduction to the SCOPE App video.
  const [expanded, setExpanded] = React.useState<string | false>("main-panel");

  const data = getHowToVideosPageState();

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
      <Accordion
        expanded={expanded === `main-panel`}
        onChange={handleChange(`main-panel`)}
      >
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1-content"
          id="panel1-header"
        >
          {data.mainVideoTitle}
        </AccordionSummary>
        <AccordionDetails>
          <IFrameDiv>
            <IFrame
              src={data.mainVideoUrl}
              title={data.mainVideoTitle}
            ></IFrame>
          </IFrameDiv>
        </AccordionDetails>
      </Accordion>
      {data.screens.map((screen, screenIdx) => (
        <React.Fragment key={screenIdx}>
          <HeaderText>{screen.screenTitle}</HeaderText>
          {screen.screenVideos.map((video, videoIdx) => (
            <Accordion
              key={videoIdx}
              expanded={expanded === `panel-${screenIdx + 1}-${videoIdx + 1}`}
              onChange={handleChange(`panel-${screenIdx + 1}-${videoIdx + 1}`)}
            >
              <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                aria-controls={`panel-${screenIdx + 1}-${videoIdx + 1}-content`}
                id={`panel-${screenIdx + 1}-${videoIdx + 1}-header`}
              >
                {video.videoTitle}
              </AccordionSummary>
              <AccordionDetails>
                <IFrameDiv>
                  <IFrame
                    src={video.videoUrl}
                    title={video.videoTitle}
                  ></IFrame>
                </IFrameDiv>
              </AccordionDetails>
            </Accordion>
          ))}
        </React.Fragment>
      ))}
      {/* This is needed to make the video work */}
      <script src="https://player.vimeo.com/api/player.js"></script>{" "}
    </DetailPage>
  );
};

export default HowToVideosPage;
