import { action, computed, makeAutoObservable } from 'mobx';
import { IAppConfig, IAssessmentContent, ILifeAreaContent, IUser } from 'shared/types';
import { PromiseQuery, PromiseState } from 'src/services/promiseQuery';
import { useServices } from 'src/services/services';
import { AuthStore, IAuthStore } from 'src/stores/AuthStore';
import { IPatientStore, PatientStore } from 'src/stores/PatientStore';

export interface IRootStore {
    // Stores
    patientStore: IPatientStore;
    authStore: IAuthStore;

    // App metadata
    appTitle: string;
    appConfig: IAppConfig;

    // UI states
    loadState: PromiseState;
    loginState: PromiseState;
    inspirationalQuote: string;

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
    public appConfig: IAppConfig;

    // UI states

    // Promise queries
    private readonly loginQuery: PromiseQuery<IUser | undefined>;
    private readonly quoteQuery: PromiseQuery<string>;
    private readonly loadQuery: PromiseQuery<PromiseSettledResult<void>[]>;

    constructor(serverConfig: IAppConfig) {
        this.patientStore = new PatientStore();
        this.authStore = new AuthStore();

        this.loginQuery = new PromiseQuery(undefined, 'loginQuery');
        this.quoteQuery = new PromiseQuery('', 'quoteQuery');
        this.loadQuery = new PromiseQuery([], 'loadQuery');

        this.appConfig = serverConfig;

        makeAutoObservable(this);
    }

    @computed
    public get loginState() {
        return this.loginQuery.state;
    }

    @computed
    public get loadState() {
        if (this.loadQuery.state == 'Pending') {
            return this.loadQuery.state;
        } else {
            return this.patientStore.loadState;
        }
    }

    @computed
    public get inspirationalQuote() {
        return this.quoteQuery.value || '';
    }

    @action.bound
    public getAssessmentContent(assessmentId: string) {
        return this.appConfig.assessments.find((s) => s.name.toLowerCase() == assessmentId.toLowerCase());
    }

    @action.bound
    public getLifeAreaContent(lifearea: string) {
        return this.appConfig.lifeAreas.find((la) => la.id == lifearea);
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
