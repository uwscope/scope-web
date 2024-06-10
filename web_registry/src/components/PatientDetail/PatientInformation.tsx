import React, { FunctionComponent } from "react";

import { Grid } from "@mui/material";
import ClinicalHistory from "src/components/PatientDetail/ClinicalHistory";
import RecentInteraction from "src/components/PatientDetail/RecentInteraction";
import { TreatmentInfo } from "src/components/PatientDetail/TreatmentInfo";

export const PatientInformation: FunctionComponent = () => {
  return (
    <Grid container spacing={3} alignItems="stretch" direction="row">
      <Grid item xs={12} sm={12} md={12} lg={12}>
        <RecentInteraction />
      </Grid>
      <Grid item xs={12} sm={6}>
        <ClinicalHistory />
      </Grid>
      <Grid item xs={12} sm={6}>
        <TreatmentInfo />
      </Grid>
    </Grid>
  );
};

export default PatientInformation;
