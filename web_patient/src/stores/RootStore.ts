import { action, computed, makeAutoObservable } from 'mobx';
import { IAppConfig, IAppContentConfig, IAssessmentContent, ILifeAreaContent, IPatientUser } from 'shared/types';
import { getPatientServiceInstance, IPatientService } from 'shared/patientService';
import { PromiseQuery, PromiseState } from 'shared/promiseQuery';
import { useServices } from 'src/services/services';
import { AuthStore, IAuthStore } from 'src/stores/AuthStore';
import { IPatientStore, PatientStore } from 'src/stores/PatientStore';

export interface IRootStore {
    // Stores
    patientStore: IPatientStore;
    authStore: IAuthStore;

    // App metadata
    appTitle: string;
    appContentConfig: IAppContentConfig;

    // UI states
    loadState: PromiseState;
    loginState: PromiseState;
    inspirationalQuote: string;

    createPatientStore: (patientService: IPatientService) => void;

    // Helpers
    getAssessmentContent: (assessmentId: string) => IAssessmentContent | undefined;
    getLifeAreaContent: (lifearea: string) => ILifeAreaContent | undefined;

    // Data load/save
    load: () => void;
}

export class RootStore implements IRootStore {
    // Stores
    public patientStore: IPatientStore;
    public authStore: IAuthStore;

    // App metadata
    public appTitle = 'SCOPE for Patients';
    public appContentConfig: IAppContentConfig;

    // UI states

    // Promise queries
    private readonly loginQuery: PromiseQuery<IPatientUser | undefined>;
    private readonly quoteQuery: PromiseQuery<string>;
    private readonly loadQuery: PromiseQuery<PromiseSettledResult<void>[]>;

    constructor(serverConfig: IAppConfig) {
        this.authStore = new AuthStore();

        // Create a dummy patient store which should fail if tried to access
        this.patientStore = new PatientStore(getPatientServiceInstance(CLIENT_CONFIG.flaskBaseUrl, 'invalid'));

        this.loginQuery = new PromiseQuery(undefined, 'loginQuery');
        this.quoteQuery = new PromiseQuery('', 'quoteQuery');
        this.loadQuery = new PromiseQuery([], 'loadQuery');

        this.appContentConfig = serverConfig.content;

        makeAutoObservable(this);
    }

    @computed
    public get loginState() {
        return this.loginQuery.state;
    }

    @computed
    public get loadState() {
        if (
            this.loadQuery.pending ||
            this.patientStore?.loadPatientState.pending ||
            this.patientStore?.loadConfigState.pending
        ) {
            return 'Pending';
        } else if (
            this.loadQuery.error ||
            this.patientStore?.loadPatientState.error ||
            this.patientStore?.loadConfigState.error
        ) {
            return 'Rejected';
        } else {
            return this.patientStore?.loadPatientState.state || 'Unknown';
        }
    }

    @computed
    public get inspirationalQuote() {
        return this.quoteQuery.value || '';
    }
    @action.bound
    public async createPatientStore(patientService: IPatientService) {
        // This is a bit twisted, but patient store/service doesn't make sense to exist until we have a patient id, and it makes more sense for the store to own the service.
        this.patientStore = new PatientStore(patientService);
    }

    @action.bound
    public getAssessmentContent(assessmentId: string) {
        return this.appContentConfig.assessments.find((s) => s.id.toLowerCase() == assessmentId.toLowerCase());
    }

    @action.bound
    public getLifeAreaContent(lifearea: string) {
        return this.appContentConfig.lifeAreas.find((la) => la.id == lifearea);
    }

    @action.bound
    public async load() {
        await this.loadQuery.fromPromise(Promise.allSettled([this.loadQuotes(), this.patientStore.load()]));
    }

    @action.bound
    public async loadQuotes() {
        const { appService } = useServices();
        const promise = appService.getInspirationalQuote();
        await this.quoteQuery.fromPromise(promise);
    }
}
