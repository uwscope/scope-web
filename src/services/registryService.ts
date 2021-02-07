import { selectRandom } from '../utils/array';
import {
    clinicCodeValues,
    discussionFlagValues,
    followupScheduleValues,
    IPatient,
    patientSexValues,
    treatmentStatusValues,
} from './types';

export interface IRegistryService {
    // TODO: async/await: Need babel polyfill
    getPatients(): IPatient[]; //Promise<IUser>;
}

class RegistryService implements IRegistryService {
    public getPatients() {
        const patientCount = getRandomInteger(3, 10);

        const patients = [...Array(patientCount).keys()].map((_) => {
            return {
                MRN: getRandomInteger(10000, 1000000),
                firstName: TEST_getRandomFirstName(),
                lastName: TEST_getRandomLastName(),
                birthdate: TEST_getRandomBirthdate(),
                sex: TEST_getRandomPatientSex(),
                primaryCareManagerName: TEST_getRandomCareManager(),
                treatmentStatus: TEST_getRandomTreatmentStatus(),
                clinicCode: TEST_getRandomClinicCode(),
                followupSchedule: TEST_getRandomFollowupSchedule(),
                discussionFlag: TEST_getRandomDiscussionFlag(),
                notes: 'blah',
            } as IPatient;
        });

        return patients; //Promise.resolve(patients);
    }
}

export const RegistryServiceInstance = new RegistryService() as IRegistryService;

// Below are temporary TEST methods for generating fake data
const TEST_getRandomPatientSex = () => {
    return patientSexValues[getRandomInteger(0, patientSexValues.length)];
};

const TEST_getRandomClinicCode = () => {
    return clinicCodeValues[getRandomInteger(0, clinicCodeValues.length)];
};

const TEST_getRandomTreatmentStatus = () => {
    return treatmentStatusValues[getRandomInteger(0, treatmentStatusValues.length)];
};

const TEST_getRandomFollowupSchedule = () => {
    return followupScheduleValues[getRandomInteger(0, followupScheduleValues.length)];
};

const TEST_getRandomDiscussionFlag = () => {
    return discussionFlagValues[getRandomInteger(0, discussionFlagValues.length)];
};

const firstNames = [
    'Paisley',
    'Vince',
    'Prudence',
    'Floyd',
    'Marty',
    'Yvonne',
    'Russ',
    'Herb',
    'Hannah',
    'Melanie',
    'Dwayne',
    'Clifford',
    'Garth',
    'Rachel',
    'Phoebe',
    'Doug',
    'Mortimer',
    'Heath',
    'Iris',
    'Tony',
];

const lastNames = [
    'Lowe',
    'Dawson',
    'Porter',
    'Tomlinson',
    'Windrow',
    'Cook',
    'Wolfe',
    'Chapman',
    'Malone',
    'Green',
    'Fairbank',
    'Wood',
    'Miller',
    'Clayton',
    'Russell',
    'Atkinson',
    'Whitehead',
    'Greene',
    'Cannon',
    'Pope',
];

const careManagers = ['Luke Skywalker', 'Leia Organa', 'Han Solo', 'Padme Amidala'];

const TEST_getRandomFirstName = () => {
    return selectRandom(firstNames);
};

const TEST_getRandomLastName = () => {
    return selectRandom(lastNames);
};

const TEST_getRandomCareManager = () => {
    return selectRandom(careManagers);
};

const TEST_getRandomBirthdate = () => {
    return new Date(getRandomInteger(1930, 2000), getRandomInteger(0, 12), getRandomInteger(1, 28));
};

const getRandomInteger = (minInclusive: number, maxExclusive: number) => {
    return Math.floor(Math.random() * (maxExclusive - minInclusive) + minInclusive);
};
