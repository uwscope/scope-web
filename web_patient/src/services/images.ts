import MyValuesInventoryImageSrc from 'src/assets/inventory.jpeg';
import MissingImageSrc from 'src/assets/missingimage.png';
import MoodLoggingImageSrc from 'src/assets/moodlogging.jpeg';
import MyNotesImageSrc from 'src/assets/mynotes.jpeg';
import MySafetyPlanImageSrc from 'src/assets/safetyplan.jpeg';

const _images = {
    Home_values_button_image: MyValuesInventoryImageSrc,
    Home_safety_button_image: MySafetyPlanImageSrc,
    Home_mood_button_image: MoodLoggingImageSrc,
    Profile_safety_button_image: MySafetyPlanImageSrc,
    Profile_notes_button_image: MyNotesImageSrc,
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
