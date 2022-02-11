import ActivityProgressImageSrc from 'src/assets/activity_icon.png';
import MissingImageSrc from 'src/assets/missingimage.png';
import MoodLoggingImageSrc from 'src/assets/mood_logging_icon.png';
import MySafetyPlanImageSrc from 'src/assets/safety_plan_icon.png';
import MyValuesInventoryImageSrc from 'src/assets/values_inventory_icon.png';
import MyWorksheetsImageSrc from 'src/assets/worksheets_icon.png';

const _images = {
    Home_values_button_image: MyValuesInventoryImageSrc,
    Home_safety_button_image: MySafetyPlanImageSrc,
    Home_mood_button_image: MoodLoggingImageSrc,
    Profile_values_button_image: MyValuesInventoryImageSrc,
    Profile_safety_button_image: MySafetyPlanImageSrc,
    Profile_worksheets_button_image: MyWorksheetsImageSrc,
    Progress_activity_button_image: ActivityProgressImageSrc,
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
