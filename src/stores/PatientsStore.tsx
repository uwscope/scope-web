import { action, computed, IObservableArray, makeAutoObservable, observable } from 'mobx';
import { AllClinicCode, ClinicCode } from 'src/services/enums';
import { PromiseQuery, PromiseState } from 'src/services/promiseQuery';
import { useServices } from 'src/services/services';
import { IPatient } from 'src/services/types';
import { IPatientStore, PatientStore } from 'src/stores/PatientStore';
import { contains, unique } from 'src/utils/array';

export interface IPatientsStore {
    readonly patients: ReadonlyArray<IPatientStore>;
    readonly careManagers: ReadonlyArray<string>;
    readonly clinics: ReadonlyArray<ClinicCode>;
    readonly filteredCareManager: string;
    readonly filteredClinic: ClinicCode | AllClinicCode;
    readonly filteredPatients: ReadonlyArray<IPatientStore>;
    readonly state: PromiseState;

    getPatients: () => void;
    filterCareManager: (careManager: string) => void;
    filterClinic: (clinic: ClinicCode | AllClinicCode) => void;
}

export class PatientsStore implements IPatientsStore {
    @observable public patients: IObservableArray<IPatientStore>;
    @observable public filteredCareManager: string;
    @observable public filteredClinic: ClinicCode | AllClinicCode;

    private readonly loadPatientsQuery: PromiseQuery<IPatient[]>;
    private readonly AllCareManagers = 'All Care Managers';

    constructor() {
        this.patients = observable.array([]);
        this.filteredCareManager = this.AllCareManagers;
        this.filteredClinic = 'All Clinics';

        this.loadPatientsQuery = new PromiseQuery([], 'loadPatients');

        makeAutoObservable(this);
    }

    @computed
    public get careManagers() {
        const cm = unique(this.patients.map((p) => p.primaryCareManagerName)).sort();
        cm.push(this.AllCareManagers);
        return cm;
    }

    @computed
    public get state() {
        return this.loadPatientsQuery.state;
    }

    @computed
    public get clinics() {
        const cc = unique(this.patients.map((p) => p.clinicCode)).sort();
        return cc;
    }

    @action.bound
    public async getPatients() {
        if (this.state != 'Pending') {
            const { registryService } = useServices();
            const promise = registryService.getPatients();
            const patients = await this.loadPatientsQuery.fromPromise(promise);
            action(() => {
                this.patients.replace(patients.map((p) => new PatientStore(p)));
                this.filterCareManager(this.filteredCareManager);
            })();
        }
    }

    @action.bound
    public filterCareManager(careManager: string) {
        if (contains(this.careManagers, careManager)) {
            this.filteredCareManager = careManager;
        } else {
            this.filteredCareManager = this.AllCareManagers;
        }
    }

    @action.bound
    public filterClinic(clinicCode: ClinicCode | AllClinicCode) {
        if (contains(this.clinics, clinicCode)) {
            this.filteredClinic = clinicCode;
        } else {
            this.filteredClinic = 'All Clinics';
        }
    }

    @computed
    public get filteredPatients() {
        var filteredPatients = this.patients.map((p) => p);
        if (this.filteredCareManager != this.AllCareManagers) {
            filteredPatients = filteredPatients.filter((p) => p.primaryCareManagerName == this.filteredCareManager);
        }

        if (this.filteredClinic != 'All Clinics') {
            filteredPatients = filteredPatients.filter((p) => p.clinicCode == this.filteredClinic);
        }

        return filteredPatients;
    }
}
