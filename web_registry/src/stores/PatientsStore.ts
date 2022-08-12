import { action, computed, makeAutoObservable, observable } from 'mobx';
import { AllClinicCode, ClinicCode, clinicCodeValues } from 'shared/enums';
import { IPatient, IProviderIdentity } from 'shared/types';
import { IPromiseQueryState, PromiseQuery } from 'shared/promiseQuery';
import { useServices } from 'src/services/services';
import { IPatientStore, PatientStore } from 'src/stores/PatientStore';
import { contains } from 'src/utils/array';
import { getLogger } from 'shared/logger';
import { getLoadAndLogQuery } from 'shared/stores';

const logger = getLogger('RegistryStore');

export interface IPatientsStore {
    readonly patients: ReadonlyArray<IPatientStore>;

    readonly careManagers: IProviderIdentity[];
    readonly psychiatrists: IProviderIdentity[];

    readonly filterableCareManagers: ReadonlyArray<string>;
    readonly filterableClinics: ReadonlyArray<string>;

    readonly filteredCareManager: string;
    readonly filteredClinic: ClinicCode | AllClinicCode;
    readonly filteredStudyPatients: boolean;

    readonly filteredPatients: ReadonlyArray<IPatientStore>;

    readonly state: IPromiseQueryState;

    load: (getToken?: () => string | undefined, onUnauthorized?: () => void) => Promise<void>;

    addPatient: (patient: Partial<IPatient>) => void;
    getPatientByRecordId: (recordId: string | undefined) => IPatientStore | undefined;

    filterCareManager: (careManager: string) => void;
    filterClinic: (clinic: ClinicCode | AllClinicCode) => void;
    filterStudyPatients: (filter: boolean) => void;
}

export const AllCareManagers = 'All Social Workers';
export const AllClinics = 'All Clinics';

export class PatientsStore implements IPatientsStore {
    @observable public filteredCareManager: string;
    @observable public filteredClinic: ClinicCode | AllClinicCode;
    // Default to filtering patients who are no longer in the study
    @observable public filteredStudyPatients: boolean = true;

    private readonly loadPatientsQuery: PromiseQuery<IPatientStore[]>;
    private readonly loadProvidersQuery: PromiseQuery<IProviderIdentity[]>;
    private readonly addPatientQuery: PromiseQuery<IPatient>;

    private loadAndLogQuery: <T>(
        queryCall: () => Promise<T>,
        promiseQuery: PromiseQuery<T>,
        onConflict?: (responseData?: any) => T,
    ) => Promise<void>;

    constructor() {
        this.filteredCareManager = AllCareManagers;
        this.filteredClinic = AllClinics;

        const { registryService } = useServices();
        this.loadAndLogQuery = getLoadAndLogQuery(logger, registryService);

        this.loadPatientsQuery = new PromiseQuery([], 'loadPatients');
        this.loadProvidersQuery = new PromiseQuery([], 'loadProviders');
        this.addPatientQuery = new PromiseQuery<IPatient>(undefined, 'addPatient');

        makeAutoObservable(this);
    }

    @computed
    public get patients() {
        return this.loadPatientsQuery.value || [];
    }

    @computed
    public get careManagers() {
        return (this.loadProvidersQuery.value || []).filter((p) => p.role == 'socialWorker').map((p) => ({ ...p }));
    }

    @computed
    public get filterableCareManagers() {
        return this.careManagers.map((c) => c.name).concat([AllCareManagers]);
    }

    @computed
    public get psychiatrists() {
        return (this.loadProvidersQuery.value || []).filter((p) => p.role == 'psychiatrist').map((p) => ({ ...p }));
    }

    public get filterableClinics() {
        return [...clinicCodeValues, AllClinics];
    }

    @computed
    public get state() {
        const error = this.loadPatientsQuery.error || this.loadProvidersQuery.error;
        const pending = this.loadPatientsQuery.pending || this.loadProvidersQuery.pending;
        const fulfilled = this.loadPatientsQuery.state == 'Fulfilled' && this.loadProvidersQuery.state == 'Fulfilled';

        return {
            state: pending ? 'Pending' : error ? 'Rejected' : fulfilled ? 'Fulfilled' : 'Unknown',
            error: error,
            pending: pending,
            done: fulfilled || error,
            resetState: () => {
                this.loadPatientsQuery.resetState();
                this.loadProvidersQuery.resetState();
            },
        } as IPromiseQueryState;
    }

    @action.bound
    public async load(getToken?: () => string | undefined, onUnauthorized?: () => void) {
        const { registryService } = useServices();

        // Don't load if it's already loading
        if (this.loadPatientsQuery.pending) {
            return;
        }

        const getPatientsPromise = () =>
            registryService.getPatients().then((patients) =>
                patients.map((p) => {
                    const patientStore = new PatientStore(p);
                    patientStore.load(getToken, onUnauthorized);
                    return patientStore;
                }),
            );

        await Promise.all([
            this.loadAndLogQuery<IPatientStore[]>(getPatientsPromise, this.loadPatientsQuery),
            this.loadAndLogQuery<IProviderIdentity[]>(registryService.getProviders, this.loadProvidersQuery),
        ]);
    }

    @action.bound
    public async addPatient(patient: Partial<IPatient>) {
        const { registryService } = useServices();
        const promise = registryService.addPatient(patient);
        const newPatient = await this.addPatientQuery.fromPromise(promise);
        action(() => {
            this.patients.push(new PatientStore(newPatient));
            this.filterCareManager(this.filteredCareManager);
        })();
    }

    @action.bound
    public filterCareManager(careManager: string) {
        if (!!this.careManagers.find((c) => c.name == careManager)) {
            this.filteredCareManager = careManager;
        } else {
            this.filteredCareManager = AllCareManagers;
        }
    }

    @action.bound
    public filterClinic(clinicCode: ClinicCode | AllClinicCode) {
        if (contains([...clinicCodeValues], clinicCode)) {
            this.filteredClinic = clinicCode;
        } else {
            this.filteredClinic = 'All Clinics';
        }
    }

    @action.bound
    public filterStudyPatients(filter: boolean) {
        this.filteredStudyPatients = filter;
    }

    @computed
    public get filteredPatients() {
        var filteredPatients = this.patients.map((p) => p);
        if (this.filteredCareManager != AllCareManagers) {
            filteredPatients = filteredPatients.filter(
                (p) => p.profile?.primaryCareManager?.name == this.filteredCareManager,
            );
        }

        if (this.filteredClinic != 'All Clinics') {
            filteredPatients = filteredPatients.filter((p) => p.profile?.clinicCode == this.filteredClinic);
        }

        if (this.filteredStudyPatients) {
            filteredPatients = filteredPatients.filter((p) => p.profile.depressionTreatmentStatus != 'End');
        }

        return filteredPatients;
    }

    public getPatientByRecordId(recordId: string | undefined) {
        if (!!recordId) {
            const patient = this.patients.filter((p) => p.recordId == recordId)[0];

            return patient;
        }

        return undefined;
    }
}
