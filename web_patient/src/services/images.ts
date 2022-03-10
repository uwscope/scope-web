import ActivityProgressImageSrc from 'src/assets/activity_pencil.png';
import MissingImageSrc from 'src/assets/missingimage.png';
import MoodLoggingImageSrc from 'src/assets/mood_smiley.png';
import MySafetyPlanImageSrc from 'src/assets/safety_plan_icon.png';
import MyValuesInventoryImageSrc from 'src/assets/value_diamond.png';
import MyWorksheetsImageSrc from 'src/assets/resources_folder.png';
import AboutUsImageSrc from 'src/assets/about_us_icon.png';
import CrisisResourcesImageSrc from 'src/assets/crisis_resources_icon.png';
import PhqAssessmentImageSrc from 'src/assets/assessment_phq9_depression.png';
import GadAssessmentImageSrc from 'src/assets/assessment_gad7_anxiety.png';
import LogoutImageSrc from 'src/assets/log_out_icon.png';

const _images = {
    Home_values_button_image: MyValuesInventoryImageSrc,
    Home_safety_button_image: MySafetyPlanImageSrc,
    Home_mood_button_image: MoodLoggingImageSrc,
    Resources_values_button_image: MyValuesInventoryImageSrc,
    Resources_safety_button_image: MySafetyPlanImageSrc,
    Resources_worksheets_button_image: MyWorksheetsImageSrc,
    Resources_about_us_button_image: AboutUsImageSrc,
    Resources_crisis_resources_button_image: CrisisResourcesImageSrc,
    Resources_logout_button_image: LogoutImageSrc,
    Progress_activity_button_image: ActivityProgressImageSrc,
    Progress_assessment_phq_button_image: PhqAssessmentImageSrc,
    Progress_assessment_gad_button_image: GadAssessmentImageSrc,
    Progress_mood_button_image: MoodLoggingImageSrc,
};

type Images = typeof _images;

export type ImageId = keyof Images;

export const getImage = (key: ImageId) => {
    const found = _images[key];
    if (!found) {
        return MissingImageSrc;
    } else {
        return found;
    }
};
